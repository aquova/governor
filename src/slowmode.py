import asyncio, datetime, discord
from config import NO_SLOWMODE

WAIT_TIME = 300 # How long to sleep between checks, in seconds
MAX_SLOWMODE = 15 # In seconds
# Threshold between slowmode levels, arbitrary units
# NOTE: If the WAIT_TIME is adjusted, this will need to be adjusted too
THRESHOLD = 80

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
                if (channel_id not in self.channel_dict) or (channel_id in NO_SLOWMODE):
                    continue

                spoken_list = self.channel_dict[channel_id]
                spoken_set = set(spoken_list)
                metric = len(spoken_list) * (len(spoken_list) / len(spoken_set))
                slowmode = min(MAX_SLOWMODE, int(metric / THRESHOLD))

                try:
                    if channel.slowmode_delay != slowmode:
                        await channel.edit(slowmode_delay=slowmode)
                except Exception as e:
                    print(f"Exception: {str(e)}")

            self.channel_dict.clear()
