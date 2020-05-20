import datetime, discord
import db

from config import RANKS, XP_PER_LVL
from dataclasses import dataclass
from math import floor

XP_PER_MINUTE = 10
STARTING_XP = 270

@dataclass
class UserData:
    xp: int
    timestamp: datetime
    username: str
    avatar: str
    next_role_at: int

class Tracker:
    def __init__(self):
        self.user_cache = {}
        self.xp_multiplier = 1

    """
    Refresh database

    Collects up-to-date data for leaderboard members

    Input: server - Discord server object
    """
    async def refresh_db(self, server):
        leaders = db.get_leaders()

        # Iterate thru every leader on the leaderboard and collect data
        for leader in leaders:
            leader_id = leader[0]
            leader_xp = leader[1]
            user = discord.utils.get(server.members, id=leader_id)

            # Update users that are still in the server
            if user != None:
                leader_name = "{}#{}".format(user.name, user.discriminator)
                leader_avatar = user.avatar

                # NOTE: May be worth to populate the cache here as well
                db.set_user_xp(leader_id, leader_xp, leader_name, leader_avatar)
            # Otherwise, prune their username/avatar so that they don't appear on the leaderboard
            else:
                db.set_user_xp(leader_id, leader_xp, None, None)

    """
    Grant user xp

    Updates user XP, levels, and roles

    Inputs:
    user - Discord user object
    xp_add - Amount of xp to add. If None, award automatic amount from speaking
    """
    async def give_xp(self, user, xp_add=None):
        user_id = user.id
        xp = 0
        next_role = None
        curr_time = datetime.datetime.now()
        out_message = None

        if user_id not in self.user_cache:
            # First, if user is not in cache, try and fetch from DB
            xp_db = db.fetch_user_xp(user_id)

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

            # Check their last timestamp if we aren't manually adding XP
            # NOTE: Mayor Lewis used to only give XP if they spoke in a "new" minute. But that would involve rounding a datetime, and I can't be bothered.
            if xp_add == None:
                last_mes_time = user_data.timestamp
                dt = curr_time - last_mes_time
                # Users only get XP every minute, so if not enough time has elapsed, ignore them
                if dt < datetime.timedelta(minutes=1):
                    return None

            # Else, grab their data
            xp = user_data.xp
            next_role = user_data.next_role_at

        if xp_add:
            xp += xp_add
        else:
            xp += XP_PER_MINUTE * self.xp_multiplier

        # If we have earned enough XP to level up, award and find next role
        if next_role != None and xp >= next_role:
            # Find what the congratulatory message should be
            # Not very efficient, but there will likely only be a handful of ranks
            for rank in RANKS:
                rank_xp = rank["level"] * XP_PER_LVL
                if rank_xp == next_role:
                    out_message = "<@{}> {}".format(user_id, rank["message"])
                    break

            next_role = await self.check_roles(user, xp)

        username = "{}#{}".format(user.name, user.discriminator)
        avatar = user.avatar

        # Update their entry in the cache
        self.user_cache[user_id] = UserData(xp, curr_time, username, avatar, next_role)
        # Update their entry in the database
        db.set_user_xp(user_id, xp, username, avatar)

        return out_message

    """
    Check roles

    Make sure the user has the correct roles, given their XP

    Inputs:
        user - Discord user object
        xp - User's XP value - int
    """
    async def check_roles(self, user, xp):
        user_roles = user.roles
        user_role_ids = [x.id for x in user.roles]
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
                elif lowest_missing_xp == None or role_xp < lowest_missing_xp:
                    lowest_missing_xp = role_xp

        if new_roles != []:
            # Go through our new role IDs, and get the actual role objects
            for role_id in new_roles:
                role = discord.utils.get(user.guild.roles, id=role_id)
                if role != None:
                    user_roles.append(role)

            # The role list *replaces* the old list, not appends to it
            await user.edit(roles=user_roles)

        return lowest_missing_xp

    """
    Set bonus XP

    Sets the XP multiplier
    """
    async def set_bonus_xp(self):
        self.xp_multiplier = 2

    """
    Reset bonus XP

    Resets the XP multiplier
    """
    async def reset_bonus_xp(self):
        self.xp_multiplier = 1
