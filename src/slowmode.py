import asyncio, datetime, discord
from config import NO_SLOWMODE

WAIT_TIME = 150 # How long to sleep between checks, in seconds
MAX_SLOWMODE = 15 # In seconds
# Threshold between slowmode levels, arbitrary units
# NOTE: If the WAIT_TIME is adjusted, this will need to be adjusted too
THRESHOLD = 40

# The max amount slowmode can increase per cycle, in seconds
INCREASE_MAX = 3
DECREASE_MAX = 2

class Thermometer:
    def __init__(self):
        self.channel_dict = {}

    def start(self, server):
        self.server = server
        self.channels = [x for x in self.server.channels if type(x) == discord.TextChannel]
        asyncio.ensure_future(self._calc_slowmode())

    async def user_spoke(self, message):
        channel = message.channel.id
        user_id = message.author.id
        if channel in self.channel_dict:
            self.channel_dict[channel].append(user_id)
        else:
            self.channel_dict[channel] = [user_id]

    async def _calc_slowmode(self):
        while True:
            await asyncio.sleep(WAIT_TIME)

            # Iterate thru each channel, generating weighted value for each channel and adjusting slowmode if necessary
            for channel in self.channels:
                channel_id = channel.id
                # Don't modify slowmode in protected channels
                if channel_id in NO_SLOWMODE:
                    continue

                slowmode = 0
                if channel_id in self.channel_dict:
                    spoken_list = self.channel_dict[channel_id]
                    spoken_set = set(spoken_list)
                    metric = len(spoken_list) * (len(spoken_list) / len(spoken_set))
                    slowmode = int(metric / THRESHOLD)

                old_slowmode = channel.slowmode_delay
                # Ensure that new setting is below the max, and also within the increase/decrease window we allow
                slowmode = min(MAX_SLOWMODE, slowmode, old_slowmode + INCREASE_MAX)
                slowmode = max(slowmode, old_slowmode - DECREASE_MAX)

                try:
                    if old_slowmode != slowmode:
                        await channel.edit(slowmode_delay=slowmode)
                except Exception as e:
                    print(f"Exception: {str(e)}")

            self.channel_dict.clear()
