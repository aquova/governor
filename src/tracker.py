import datetime, discord
import utils

from config import RANKS, XP_PER_LVL
from dataclasses import dataclass
from math import floor

XP_PER_MINUTE = 30
STARTING_XP = 270

@dataclass
class UserData:
    xp: int
    timestamp: datetime
    next_role_at: int

class Tracker:
    def __init__(self):
        self.user_cache = {}
        self.xp_multiplier = 1

    async def user_speaks(self, user):
        user_id = user.id
        xp = 0
        next_role = None
        curr_time = datetime.datetime.now()
        out_message = None

        if user_id not in self.user_cache:
            # First, if user is not in cache, try and fetch from DB
            xp_db = utils.fetch_user_xp(user_id)

            if xp_db is not None:
                # If user is in the DB, use that value
                xp = xp_db
            else:
                # Otherwise, give them starting XP value
                xp = STARTING_XP

            # Since they weren't in the cache, make sure they have the correct roles
            next_role = await self.check_roles(user, xp)
        else:
            # If user is in cache, get that value instead
            user_data = self.user_cache[user_id]

            # Check their last timestamp.
            # Note: Mayor Lewis used to only give XP if they spoke in a "new" minute. But that would involve rounding a datetime, and I can't be bothered.
            last_mes_time = user_data.timestamp
            dt = curr_time - last_mes_time
            # Users only get XP every minute, so if not enough time has elapsed, ignore them
            if dt < datetime.timedelta(minutes=1):
                return None

            # Else, grab their data
            xp = user_data.xp
            next_role = user_data.next_role_at

        xp += XP_PER_MINUTE * self.xp_multiplier

        # If we have earned enough XP to level up, award and find next role
        if next_role != None and xp >= next_role:
            # Find what the congratulatory message should be
            # Not very efficient, but there will likely only be a handful of ranks
            for rank in RANKS:
                rank_xp = rank["level"] * XP_PER_LVL
                if rank_xp == next_role:
                    out_message = rank["message"]
                    break

            next_role = await self.check_roles(user, xp)

        # Update their entry in the cache
        self.user_cache[user_id] = UserData(xp, curr_time, next_role)
        # Update their entry in the database
        utils.set_user_xp(user_id, xp)

        return out_message

    async def check_roles(self, user, xp):
        user_roles = user.roles
        user_role_ids = [x.id for x in user.roles]
        new_roles = []
        lowest_missing_xp = None

        # This doesn't require RANKS to be in order
        for rank in RANKS:
            role_id = rank["role_id"]
            if role_id not in user_role_ids:
                role_xp = rank["level"] * XP_PER_LVL
                # If user has enough XP, give them the role
                if role_xp <= xp:
                    new_roles.append(role_id)
                # Otherwise, keep track if this should be the next role to earn
                elif lowest_missing_xp == None or role_xp < lowest_missing_xp:
                    lowest_missing_xp = role_xp

        if new_roles != []:
            # Go through our new role IDs, and get the actual role objects
            for role_id in new_roles:
                role = discord.utils.get(user.guild.roles, id=role_id)
                user_roles.append(role)

            # The role list *replaces* the old list, not appends to it
            await user.edit(roles=user_roles)

        return lowest_missing_xp

    async def set_bonus_xp(self):
        self.xp_multiplier = 2

    async def reset_bonus_xp(self):
        self.xp_multiplier = 1
