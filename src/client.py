import discord

from config import LOG_CHAN
from platforms import PlatformWidget
from pronouns import PronounWidget

from typing import cast

class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    def set_channels(self):
        self.log = cast(discord.TextChannel, self.get_channel(LOG_CHAN))

    async def setup_hook(self):
        self.add_view(PlatformWidget())
        self.add_view(PronounWidget())

    async def sync_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

my_intents = discord.Intents.all()
client = DiscordClient(intents=my_intents)
