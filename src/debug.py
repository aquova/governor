import discord
from config import DEBUG_BOT, OWNER
from utils import strip_prefix, get_command

class Debug:
    def __init__(self):
        self.debugging = False

    def check_toggle(self, message):
        prefix_removed = strip_prefix(message.content)
        if prefix_removed == "":
            return False
        command = get_command(prefix_removed)
        return command == "debug"

    async def toggle_debug(self, message):
        if message.author.id == OWNER and not DEBUG_BOT:
            self.debugging = not self.debugging
            enable_mes = "enabled" if self.debugging else "disabled"
            dbg_mes = f"Debugging {enable_mes}"
            await message.channel.send(dbg_mes)

    def should_ignore_message(self, message):
        if self.debugging and message.author.id == OWNER:
            # If debugging, the live bot should ignore the owner
            return True
        elif DEBUG_BOT and message.author.id != OWNER:
            # If the debug bot, then ignore everyone else besides the owner
            return True
        else:
            return False
