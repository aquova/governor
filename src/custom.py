import discord

import commonbot.utils
import db
from client import client
from commonbot.user import UserLookup
from config import (ADMIN_ACCESS, CMD_PREFIX, LIMIT_CHANS, SERVER_URL)
from utils import CustomCommandFlags

ul = UserLookup()

"""
Is allowed

Checks if the given command is allowed to be sent in the given channel
"""
def is_allowed(cmd: str, channel_id: int) -> bool:
    commands = db.get_custom_cmds()
    if cmd not in commands:
        return False
    response = commands[cmd]
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
def parse_response(message: discord.Message) -> str:
    prefix_removed = commonbot.utils.strip_prefix(message.content, CMD_PREFIX)
    command = commonbot.utils.get_first_word(prefix_removed).lower()
    commands = db.get_custom_cmds()
    response = commands[command][0]

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
async def define_cmd(name, response: str, author: discord.User | discord.Member) -> str:
    flags = CustomCommandFlags.NONE
    is_admin = commonbot.utils.check_roles(author, ADMIN_ACCESS)

    if is_admin:
        flags |= CustomCommandFlags.ADMIN

    commands = db.get_custom_cmds()
    # Store what the command used to say, if anything
    old_response = None
    if name in commands:
        # Protect commands originally made by moderators
        if (commands[name][1] & CustomCommandFlags.ADMIN) and not is_admin:
            return f"`{name}` was created by a moderator, and only moderators can edit its contents."
        old_response = commands[name][0]

    db.set_new_custom_cmd(name, response, flags)

    # Format confirmation to the user
    output_message = f"New command added! You can use it like `{CMD_PREFIX}{name}`. "

    user_name = str(author)
    # If user allows embedding of a ping, list various ways this can be done
    if "%mention%" in response:
        user_id = author.id
        output_message += f"You can also use it as `{CMD_PREFIX}{name} {user_id}`, `{CMD_PREFIX}{name} {user_name}`, or `{CMD_PREFIX}{name} @{user_name}`"

    log_msg = ""
    if old_response:
        log_msg = f"{user_name} has changed the command `{name}` from `{old_response}` to `{response}`"
    else:
        log_msg = f"{user_name} has added the `{name}` command - `{response}`"

    await client.log.send(log_msg)

    return output_message

"""
Remove command

Removes a user-defined command
"""
async def remove_cmd(name: str, author: discord.User | discord.Member) -> str:
    # If this command did exist, remove it from cache and database
    commands = db.get_custom_cmds()
    if name in commands:
        old_msg = commands[name]
        db.remove_custom_cmd(name)
        log_msg = f"{str(author)} has removed the `{name}` command. It used to say `{old_msg}`."
        await client.log.send(log_msg)
        return f"`{name}` removed as a custom command!"
    return f"`{name}` was never a command..."

"""
Limit command

Toggles limiting a command from being used in certain channels
"""
def limit_cmd(name: str) -> str:
    commands = db.get_custom_cmds()
    if name in commands:
        response = commands[name]
        flag = response[1]
        # XOR to toggle that flag
        flag ^= CustomCommandFlags.LIMITED
        db.set_new_custom_cmd(name, response[0], flag)
        toggle_txt = "limited" if (flag & CustomCommandFlags.LIMITED) else "not limited"
        return f"`{name}` is now {toggle_txt} to certain channels"
    return f"`{name}` is not a known command."

"""
List commands

Give a list of all user-defined commands
"""
def list_cmds() -> str:
    return f"You can see a full list of commands and their responses here: {SERVER_URL}/commands.php"
