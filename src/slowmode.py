import discord
from discord.ext import commands, tasks

from config import NO_SLOWMODE

WAIT_TIME = 120 # How long to sleep between checks, in seconds
MAX_SLOWMODE = 15 # In seconds
THRESHOLD = 100 # Threshold between slowmode levels, arbitrary units

# The max amount slowmode can increase per cycle, in seconds
INCREASE_MAX = 4
DECREASE_MAX = 2

class Thermometer(commands.Cog):
    def __init__(self, guild: discord.Guild):
        self.channel_dict = {}
        self.channels = guild.text_channels
        self._calc_slowmode.start()

    def cog_unload(self):
        self._calc_slowmode.cancel()

    async def user_spoke(self, message: discord.Message):
        channel = message.channel.id
        user_id = message.author.id
        if channel in self.channel_dict:
            self.channel_dict[channel].append(user_id)
        else:
            self.channel_dict[channel] = [user_id]

    @tasks.loop(seconds=WAIT_TIME)
    async def _calc_slowmode(self):
        # Iterate thru each channel, generating weighted value for each channel and adjusting slowmode if necessary
        for channel in self.channels:
            channel_id = channel.id
            # Don't modify slowmode in protected channels
            if channel_id in NO_SLOWMODE:
                continue

            slowmode = 0
            if channel_id in self.channel_dict:
                spoken_list = self.channel_dict[channel_id]
                metric = len(spoken_list) * len(spoken_list)
                slowmode = int(metric / THRESHOLD)

            old_slowmode = channel.slowmode_delay
            # Ensure that new setting is below the max, and also within the increase/decrease window we allow
            slowmode = min(MAX_SLOWMODE, slowmode, old_slowmode + INCREASE_MAX)
            slowmode = max(slowmode, old_slowmode - DECREASE_MAX)

            if old_slowmode != slowmode:
                try:
                    await channel.edit(slowmode_delay=slowmode)
                except discord.errors.Forbidden:
                    pass
        self.channel_dict.clear()
