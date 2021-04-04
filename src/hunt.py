import discord, sqlite3
import utils
from db import inc_hunter, get_hunters

class EggHunt:
    def __init__(self):
        self.watched_channel = None
        self.hunters = set()

    def is_currently_hunting(self):
        return self.watched_channel != None

    def is_channel_watched(self, channel_id):
        if self.is_currently_hunting():
            return self.watched_channel.id == channel_id
        else:
            return False

    def set_watched_channel(self, channel):
        self.watched_channel = channel

    def add_reaction(self, user):
        self.hunters.add(user)

    @utils.requires_admin
    async def start_hunt(self, message):
        if not self.is_currently_hunting():
            self.set_watched_channel(message.channel)
            return "The hunt has begun!"
        else:
            return f"There is already an open hunt in <#{self.watched_channel.id}>. It must be stopped before another can start."

    @utils.requires_admin
    async def end_hunt(self, message):
        if not self.is_currently_hunting():
            return "Um... there was no hunt in progress"
        else:
            for user in self.hunters:
                inc_hunter(user.id, f"{user.name}#{user.discriminator}")

            self.watched_channel = None
            self.hunters.clear()
            return "Hunt concluded!"

