from datetime import datetime, timedelta, timezone
from typing import cast

import discord
from discord.ext import commands, tasks

import db
from config import RANKS, XP_PER_LVL, XP_PER_MINUTE

class Tracker(commands.Cog):
    def __init__(self):
        self.user_cache: dict[int, db.UserData] = {}
        # Maps uids to their index in RANKS
        self.role_cache: dict[int, int] = {}
        self.xp_multiplier = 1

    def setup(self, guild: discord.Guild):
        self.server = guild
        self._refresh_db.start()

    def cog_unload(self) -> None:
        self._refresh_db.cancel()

    @tasks.loop(hours=24)
    async def _refresh_db(self):
        all_leaders = db.get_leaders()
        self._refresh_helper(all_leaders)
        monthly_leaders = db.get_monthly_leaders()
        self._refresh_helper(monthly_leaders)

    def _refresh_helper(self, leaders: list[db.UserData]):
        # Iterate thru every leader on the leaderboard and collect data
        for leader_data in leaders:
            user = discord.utils.get(self.server.members, id=leader_data.uid)

            # Update users that are still in the server
            if user is not None:
                db.set_user_data(user, leader_data)
            # Otherwise, prune their username/avatar so that they don't appear on the leaderboard
            else:
                db.prune_leader(leader_data.uid)

    async def add_xp(self, user: discord.Member, xp: int) -> str:
        await self._give_xp(user, xp, True)
        return f"{xp} XP given to {str(user)}"

    async def give_default_xp(self, user: discord.Member) -> str:
        return await self._give_xp(user, XP_PER_MINUTE * self.xp_multiplier, False)

    async def _give_xp(self, user: discord.Member, xp_add: int, manual: bool) -> str:
        curr_time = datetime.now(timezone.utc)

        if user.id not in self.user_cache:
            self.user_cache[user.id] = db.fetch_user_data(user.id)

        if user.id not in self.role_cache:
            # This is the highest role *they have*, not the highest they should
            # We'll check and remedy that in a moment, if needed
            role_ids = [x.id for x in user.roles]
            best_idx = 0
            for idx in range(0, len(RANKS))[::-1]:
                if RANKS[idx]['role_id'] in role_ids:
                    best_idx = idx
                    break
            self.role_cache[user.id] = best_idx

        user_data = self.user_cache[user.id]
        role_idx = self.role_cache[user.id]

        # Check their last timestamp if we aren't manually adding XP
        if not manual:
            dt = curr_time - user_data.timestamp
            # Users only get XP every minute, so if not enough time has elapsed, ignore them
            if dt < timedelta(minutes=1):
                return ""

        # Check if we've rolled over to a new month
        if user_data.timestamp.month != curr_time.month or user_data.timestamp.year != curr_time.year:
            user_data.monthly_xp = 0

        user_data.xp += xp_add
        if not manual:
            # We don't consider manually added XP as part of the monthly total
            user_data.monthly_xp += xp_add

        ret = ""
        # If they haven't maxed out their roles, and have enough XP for the next one, grant that Discord role and post messages
        if role_idx < len(RANKS) - 1:
            next_xp = RANKS[role_idx + 1]['level'] * XP_PER_LVL
            if next_xp < user_data.xp:
                role_idx += 1
                self.role_cache[user.id] = role_idx
                roles = user.roles
                new_role = discord.utils.get(user.guild.roles, id=RANKS[role_idx]['role_id'])
                if new_role is not None:
                    roles.append(new_role)
                    await user.edit(roles=roles)
                # Some ranks have special messages, either for the user or for a new channel they've just unlocked
                if RANKS[role_idx]['message'] != "":
                    ret = f"<@{user.id}> {RANKS[role_idx]['message']}"
                if RANKS[role_idx]['welcome']['message'] != "":
                    for welcome_id in RANKS[role_idx]['welcome']['channels']:
                        chan = cast(discord.TextChannel, self.server.get_channel(welcome_id))
                        if chan is not None:
                            await chan.send(f"Hello <@{user.id}>! {RANKS[role_idx]['welcome']['message']}")

        self.user_cache[user.id] = user_data
        self.role_cache[user.id] = role_idx
        db.set_user_data(user, user_data)
        return ret

    async def bring_up_user(self, user: discord.Member):
        # When a user joins the server, give them any roles they need
        user_data = db.fetch_user_data(user.id)
        roles = user.roles
        role_ids = [x.id for x in user.roles]
        for idx in range(0, len(RANKS)):
            if RANKS[idx]['level'] * XP_PER_LVL < user_data.xp and RANKS[idx]['role_id'] not in role_ids:
                new_role = discord.utils.get(user.guild.roles, id=RANKS[idx]['role_id'])
                if new_role is not None:
                    roles.append(new_role)
        await user.edit(roles=roles)

    def remove_from_cache(self, uid: int):
        if uid in self.user_cache:
            del self.user_cache[uid]
        if uid in self.role_cache:
            del self.role_cache[uid]

    async def set_bonus_xp(self, enabled: bool) -> str:
        if enabled:
            self.xp_multiplier = 2
            return "XP multiplier is now x2!"
        else:
            self.xp_multiplier = 1
            return "XP multiplier has been reset"
