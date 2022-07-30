import discord

from pronouns import PronounWidget

class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(PronounWidget())

    async def sync_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

my_intents = discord.Intents.all()
client = DiscordClient(intents=my_intents)
