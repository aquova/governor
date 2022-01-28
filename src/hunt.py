import discord, sqlite3

from db import inc_hunter, get_hunters
from utils import requires_admin

class EggHunt:
    def __init__(self):
        self.creator = None
        self.watched_channel = None
        self.hunters = set()

    def is_currently_hunting(self) -> bool:
        return self.watched_channel != None

    def is_channel_watched(self, channel_id: int) -> bool:
        if self.is_currently_hunting():
            return self.watched_channel.id == channel_id
        else:
            return False

    def set_watched_channel(self, channel: discord.TextChannel):
        self.watched_channel = channel

    def add_reaction(self, user: discord.Member):
        if self.creator != user:
            self.hunters.add(user)

    @requires_admin
    async def start_hunt(self, message: discord.Message) -> str:
        if not self.is_currently_hunting():
            self.creator = message.author
            self.set_watched_channel(message.channel)
            return "The hunt has begun!"
        else:
            return f"There is already an open hunt in <#{self.watched_channel.id}>. It must be stopped before another can start."

    @requires_admin
    async def end_hunt(self, message: discord.Message) -> str:
        if not self.is_currently_hunting():
            return "Um... there was no hunt in progress"
        else:
            for user in self.hunters:
                inc_hunter(user.id, f"{user.name}#{user.discriminator}")

            self.creator = None
            self.watched_channel = None
            self.hunters.clear()
            return "Hunt concluded!"

