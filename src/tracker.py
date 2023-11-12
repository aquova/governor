from datetime import datetime, timedelta
from typing import cast

import discord
from discord.ext import commands, tasks

import db
from client import client
from commonbot.user import UserLookup
from config import CMD_PREFIX, RANKS, XP_PER_LVL, XP_PER_MINUTE
from utils import requires_admin

class UserData:
    def __init__(self, xp: int, monthly_xp: int, timestamp: datetime, username: str, avatar: str, next_role_at: int | None):
        self.xp = xp
        self.monthly_xp = monthly_xp
        self.timestamp = timestamp
        self.username = username
        self.avatar = avatar
        self.next_role_at = next_role_at

class Tracker(commands.Cog):
    def __init__(self, guild: discord.Guild):
        self.user_cache = {}
        self.xp_multiplier = 1
        self.ul = UserLookup()
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

    def _refresh_helper(self, leaders: list[tuple]):
        # Iterate thru every leader on the leaderboard and collect data
        for leader in leaders:
            leader_id = leader[0]
            leader_xp = leader[1]
            leader_monthly = leader[4]
            leader_month = leader[5]
            leader_year = leader[6]
            user = discord.utils.get(self.server.members, id=leader_id)

            # Update users that are still in the server
            if user:
                try:
                    # NOTE: May be worth to populate the cache here as well
                    avatar = user.display_avatar.replace(size=64, format="gif", static_format="webp")
                    db.set_user_xp(leader_id, leader_xp, str(user), avatar.url, leader_monthly, leader_month, leader_year, str(user.color))
                except ValueError as e:
                    print(str(e))
            # Otherwise, prune their username/avatar so that they don't appear on the leaderboard
            else:
                db.set_user_xp(leader_id, leader_xp, None, None, leader_monthly, leader_month, leader_year, None)

    """
    Grant user xp

    Updates user XP, levels, and roles
    """
    async def give_xp(self, user: discord.Member | discord.User, xp_add: int | None=None) -> str | None:
        user_id = user.id
        xp = 0
        monthly_xp = 0
        next_role = None
        curr_time = datetime.now()
        out_message = None

        if user_id not in self.user_cache:
            xp = db.fetch_user_xp(user_id)
            monthly_xp = db.fetch_user_monthly_xp(user_id)

            # Since they weren't in the cache, make sure they have the correct roles
            next_role = await self._check_roles(user, xp)
        else:
            # If user is in cache, get that value instead
            user_data = self.user_cache[user_id]
            last_mes_time = user_data.timestamp

            # Check their last timestamp if we aren't manually adding XP
            # NOTE: Mayor Lewis used to only give XP if they spoke in a "new" minute. But that would involve rounding a datetime, and I can't be bothered.
            if not xp_add:
                dt = curr_time - last_mes_time
                # Users only get XP every minute, so if not enough time has elapsed, ignore them
                if dt < timedelta(minutes=1):
                    return None

            # Else, grab their data
            xp = user_data.xp
            monthly_xp = user_data.monthly_xp
            next_role = user_data.next_role_at

            # Check if we've rolled over to a new month
            if last_mes_time.month != curr_time.month or last_mes_time.year != curr_time.year:
                monthly_xp = 0

        if not xp_add:
            new_xp = XP_PER_MINUTE * self.xp_multiplier
            monthly_xp += new_xp
            xp += new_xp
        else:
            xp += xp_add

        # If we have earned enough XP to level up, award and find next role
        if next_role and xp >= next_role:
            # Find what the congratulatory message should be
            # Not very efficient, but there will likely only be a handful of ranks
            for rank in RANKS:
                rank_xp = rank["level"] * XP_PER_LVL
                if rank_xp == next_role:
                    if rank['message'] != "":
                        out_message = f"<@{user_id}> {rank['message']}"

                    if rank['welcome']['message'] != "":
                        for welcome_id in rank['welcome']['channels']:
                            chan = cast(discord.TextChannel, client.get_channel(welcome_id))
                            if chan is not None:
                                await chan.send(f"Hello <@{user_id}>! {rank['welcome']['message']}")
                    break

            next_role = await self._check_roles(user, xp)

        try:
            avatar = user.display_avatar.replace(size=64, format="gif", static_format="webp")
            # Update their entry in the cache
            self.user_cache[user_id] = UserData(xp, monthly_xp, curr_time, str(user), avatar.url, next_role)
            # Update their entry in the database
            db.set_user_xp(user_id, xp, str(user), avatar.url, monthly_xp, curr_time.month, curr_time.year, str(user.color))
        except ValueError as e:
            print(str(e))

        return out_message

    """
    Check roles

    Make sure the user has the correct roles, given their XP
    """
    async def _check_roles(self, user: discord.Member | discord.User, xp: int) -> int | None:
        if isinstance(user, discord.User):
            return None

        try:
            user_roles = user.roles
            user_role_ids = [x.id for x in user.roles]
        except AttributeError:
            user_roles = []
            user_role_ids = []

        new_roles = []
        lowest_missing_xp = None

        # This doesn't require RANKS to be in order
        for rank in RANKS:
            role_id = rank["role_id"]
            # If they're missing a role, check if they qualify
            if role_id not in user_role_ids:
                role_xp = rank["level"] * XP_PER_LVL
                # If user has enough XP, give them the role
                if role_xp <= xp:
                    new_roles.append(role_id)
                # Otherwise, keep track if this should be the next role to earn
                elif lowest_missing_xp is None or role_xp < lowest_missing_xp:
                    lowest_missing_xp = role_xp

        if new_roles:
            # Go through our new role IDs, and get the actual role objects
            for role_id in new_roles:
                role = discord.utils.get(user.guild.roles, id=role_id)
                if role:
                    user_roles.append(role)

            # The role list *replaces* the old list, not appends to it
            await user.edit(roles=user_roles)

        return lowest_missing_xp

    """
    Remove item from cache

    Removes a user from the user cache, in the event they leave the server
    """
    def remove_from_cache(self, user_id: int):
        if user_id in self.user_cache:
            del self.user_cache[user_id]

    """
    Add XP

    Adds the specified amout of XP to a user
    """
    @requires_admin
    async def add_xp(self, message: discord.Message) -> str:
        try:
            guild = message.guild
            if guild is None:
                return ""
            # Treat last word as XP to be awarded
            xp = int(message.content.split(" ")[-1])
            userid = self.ul.parse_id(message)
            # Incase they didn't give an XP, don't parse ID as XP lol
            if xp == userid:
                return "Was unable to find XP value in that message"
            user = discord.utils.get(guild.members, id=userid)
            if user is not None:
                await self.give_xp(user, xp)
                return f"{xp} XP given to {str(user)}"
            else:
                return "Was unable to find that user in the server"
        except (IndexError, ValueError):
            return f"`{CMD_PREFIX}addxp USER XP`"

    """
    Set bonus XP

    Sets the XP multiplier
    """
    @requires_admin
    async def set_bonus_xp(self, _) -> str:
        self.xp_multiplier = 2
        return "XP multiplier is now x2!"

    """
    Reset bonus XP

    Resets the XP multiplier
    """
    @requires_admin
    async def reset_bonus_xp(self, _) -> str:
        self.xp_multiplier = 1
        return "XP multiplier has been reset"

