import discord
from pronouns import PronounWidget

class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

    async def setup_hook(self):
        self.add_view(PronounWidget())

my_intents = discord.Intents.all()
client = DiscordClient(intents=my_intents)
