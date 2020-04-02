import datetime, discord
import utils
from dataclasses import dataclass

XP_PER_MINUTE = 30
STARTING_XP = 270

@dataclass
class UserData:
    xp: int
    timestamp: datetime

class Tracker:
    def __init__(self):
        self.user_cache = {}
        self.xp_multiplier = 1

    def user_speaks(self, user_id):
        xp = 0
        curr_time = datetime.datetime.now()

        if user_id not in self.user_cache:
            # First, if user is not in cache, try and fetch from DB
            xp_db = utils.fetch_user_xp(user_id)

            if xp_db is not None:
                # If user is in the DB, use that value
                xp = xp_db
            else:
                # Otherwise, give them starting XP value
                xp = STARTING_XP
        else:
            # If user is in cache, get that value instead
            user_data = self.user_cache[user_id]

            # Check their last timestamp.
            # Note: Mayor Lewis used to only give XP if they spoke in a "new" minute. But that would involve rounding a datetime, and I can't be bothered.
            last_mes_time = user_data.timestamp
            dt = curr_time - last_mes_time
            # Users only get XP every minute, so if not enough time has elapsed, ignore them
            if dt < datetime.timedelta(minutes=1):
                return

            # Else, grab their XP
            xp = user_data.xp

        xp += XP_PER_MINUTE * self.xp_multiplier

        # Update their entry in the cache
        self.user_cache[user_id] = UserData(xp, curr_time)
        # Update their entry in the database
        utils.set_user_xp(user_id, xp)

    def bonus_xp(self):
        self.xp_multiplier = 2

    def reset_multiplier(self):
        self.xp_multiplier = 1
