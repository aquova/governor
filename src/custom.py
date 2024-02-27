import discord

import db
from client import client
from config import (ADMIN_ACCESS, CMD_PREFIX, LIMIT_CHANS, SERVER_URL)
from utils import CustomCommandFlags, check_roles

class DefineModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Define a new custom command")
        self.name = discord.ui.TextInput(
            label="Command Name",
            style=discord.TextStyle.short,
            required=True
        )
        self.response = discord.ui.TextInput(
            label="Command Response",
            style=discord.TextStyle.long,
            max_length=1999,
            required=True
        )
        self.add_item(self.name)
        self.add_item(self.response)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value.lower()
        response = self.response.value
        flags = CustomCommandFlags.NONE
        is_admin = check_roles(interaction.user, ADMIN_ACCESS)

        if is_admin:
            flags |= CustomCommandFlags.ADMIN

        commands = db.get_custom_cmds()
        # Store what the command used to say, if anything
        old_response = None
        if name in commands:
            old_response = commands[name][0]

        db.set_new_custom_cmd(name, response, flags)

        # Format confirmation to the user
        output_message = f"New command added! You can use it like `{CMD_PREFIX}{name}`. "

        log_msg = ""
        if old_response:
            log_msg = f"{str(interaction.user)} has changed the command `{name}` from `{old_response}` to `{response}`"
        else:
            log_msg = f"{str(interaction.user)} has added the `{name}` command - `{response}`"

        await client.log.send(log_msg)
        await interaction.response.send_message(output_message)

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
def parse_response(command) -> str:
    commands = db.get_custom_cmds()
    response = commands[command][0]
    return response

"""
Add Alias

Adds an alias to a pre-existing command
"""
def add_alias(command: str, alias: str) -> str:
    cmds = db.get_custom_cmds(False)
    if command not in cmds:
        return "I cannot make an alias for a command that does not exist"
    db.set_new_alias(alias, command)
    return f"`{alias}` is now an alias for `{command}`!"

"""
Remove command

Removes a user-defined command
"""
async def remove_cmd(name: str, author: discord.User | discord.Member) -> str:
    # First check if the command was an alias, as that is simpler to remove
    aliases = db.get_aliases()
    if name in aliases:
        db.remove_alias(name)
        log_msg = f"{str(author)} has removed the `{name}` alias. It used to point to `{aliases[name]}`."
        await client.log.send(log_msg)
        return f"The `{name}` alias has been removed!"

    # If the command exists, remove both it and any aliases pointing to it
    commands = db.get_custom_cmds(False)
    if name in commands:
        db.remove_custom_cmd(name)
        log_msg = f"{str(author)} has removed the `{name}` command, and any aliases it had. It used to say `{commands[name]}`."
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
