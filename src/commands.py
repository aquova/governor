import discord

import commonbot.utils
import db
from client import client
from commonbot.user import UserLookup
from config import (ADMIN_ACCESS, CMD_PREFIX, LIMIT_CHANS, SERVER_URL)
from utils import CustomCommandFlags, requires_admin, requires_define

ul = UserLookup()

class CustomCommands:
    def __init__(self):
        self.cmd_dict = db.get_custom_cmds()

    """
    Set Protected Keywords

    Sets the list of protected keywords that can't be used for custom command names
    """
    def set_protected_keywords(self, keywords: list[str]):
        self.keywords = keywords
        # "Debug" isn't in the command list, but also needs to be protected
        self.keywords.append('debug')

    """
    Command Available

    Checks if the custom command exists
    """
    def command_available(self, cmd: str) -> bool:
        return cmd in self.cmd_dict

    """
    Is allowed

    Checks if the given command is allowed to be sent in the given channel
    """
    def is_allowed(self, cmd: str, channel_id: int) -> bool:
        if not self.command_available(cmd):
            return False

        response = self.cmd_dict[cmd]
        limited = response[1] & CustomCommandFlags.LIMITED
        if not limited:
            return True
        elif channel_id in LIMIT_CHANS:
            return False
        return True

    """
    Parse Response

    Return the specified response for a custom command
    """
    def parse_response(self, message: discord.Message) -> str:
        prefix_removed = commonbot.utils.strip_prefix(message.content, CMD_PREFIX)
        command = commonbot.utils.get_first_word(prefix_removed).lower()
        response = self.cmd_dict[command][0]

        # Check if they want to embed a ping within the response
        mentioned_id = ul.parse_id(message)
        if mentioned_id is not None:
            ping = f"<@!{mentioned_id}>"
        else:
            ping = ""

        response = response.replace("%mention%", ping)
        return response

    """
    Define command

    Sets a new user-defined command
    """
    @requires_define
    async def define_cmd(self, message: discord.Message) -> str:
        # First remove the "define" command
        new_cmd = commonbot.utils.strip_words(message.content, 1)
        # Then parse the new command
        cmd = commonbot.utils.get_first_word(new_cmd).lower()
        response = commonbot.utils.strip_words(new_cmd, 1)
        flags = CustomCommandFlags.NONE
        is_admin = commonbot.utils.check_roles(message.author, ADMIN_ACCESS)

        if is_admin:
            flags |= CustomCommandFlags.ADMIN

        if response == "":
            # Don't allow blank responses
            return "...You didn't specify what that command should do."
        elif cmd in self.keywords:
            # Don't allow users to set commands with protected keywords
            return f"`{cmd}` is already in use as a built-in function. Please choose another name."

        # Store what the command used to say, if anything
        old_response = None
        if cmd in self.cmd_dict:
            # Protect commands originally made by moderators
            if (self.cmd_dict[cmd][1] & CustomCommandFlags.ADMIN) and not is_admin:
                return f"`{cmd}` was created by a moderator, and only moderators can edit its contents."
            old_response = self.cmd_dict[cmd][0]

        # Set new command in cache and database
        self.cmd_dict[cmd] = (response, flags)
        db.set_new_custom_cmd(cmd, response, flags)

        # Format confirmation to the user
        output_message = f"New command added! You can use it like `{CMD_PREFIX}{cmd}`. "

        author = message.author
        user_name = str(author)
        # If user allows embedding of a ping, list various ways this can be done
        if "%mention%" in response:
            user_id = author.id
            output_message += f"You can also use it as `{CMD_PREFIX}{cmd} {user_id}`, `{CMD_PREFIX}{cmd} {user_name}`, or `{CMD_PREFIX}{cmd} @{user_name}`"

        log_msg = ""
        if old_response:
            log_msg = f"{user_name} has changed the command `{cmd}` from `{old_response}` to `{response}`"
        else:
            log_msg = f"{user_name} has added the `{cmd}` command - `{response}`"

        await client.log.send(log_msg)

        return output_message

    """
    Remove command

    Removes a user-defined command
    """
    @requires_admin
    async def remove_cmd(self, message: discord.Message) -> str:
        # First remove the "define" command
        new_cmd = commonbot.utils.strip_words(message.content, 1)
        # Then parse the command to remove
        cmd = commonbot.utils.get_first_word(new_cmd).lower()

        # If this command did exist, remove it from cache and database
        if self.command_available(cmd):
            old_msg = self.cmd_dict[cmd]

            del self.cmd_dict[cmd]
            db.remove_custom_cmd(cmd)

            log_msg = f"{str(message.author)} has removed the `{cmd}` command. It used to say `{old_msg}`."
            await client.log.send(log_msg)

            return f"`{cmd}` removed as a custom command!"

        return f"`{cmd}` was never a command..."

    """
    Limit command

    Toggles limiting a command from being used in certain channels
    """
    @requires_admin
    async def limit_cmd(self, message: discord.Message) -> str:
        stripped = commonbot.utils.strip_words(message.content, 1)
        cmd = commonbot.utils.get_first_word(stripped).lower()

        if self.command_available(cmd):
            response = self.cmd_dict[cmd]
            flag = response[1]
            # XOR to toggle that flag
            flag ^= CustomCommandFlags.LIMITED
            self.cmd_dict[cmd] = (response[0], flag)
            db.set_new_custom_cmd(cmd, response[0], flag)

            toggle_txt = "limited" if (flag & CustomCommandFlags.LIMITED) else "not limited"

            return f"`{cmd}` is now {toggle_txt} to certain channels"

        return f"`{cmd}` is not a known command."

    """
    List commands

    Give a list of all user-defined commands
    """
    async def list_cmds(self, _) -> str:
        return f"You can see a full list of commands and their responses here: {SERVER_URL}/commands.php"
