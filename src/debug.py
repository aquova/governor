import discord
from config import DEBUG_BOT, OWNER

class Debug:
    def __init__(self):
        self.debugging = False

    async def toggle_debug(self, message):
        if message.author.id == OWNER and not DEBUG_BOT:
            self.debugging = not self.debugging
            return "Debugging {}".format("enabled" if self.debugging else "disabled")

    def should_ignore_message(self, message):
        if self.debugging and message.author.id == OWNER:
            # If debugging, the live bot should ignore the owner
            return True
        elif DEBUG_BOT and message.author.id != OWNER:
            # If the debug bot, then ignore everyone else besides the owner
            return True
        else:
            return False
