import discord

import db
from client import client
from config import (ADMIN_ACCESS, CMD_PREFIX, LIMIT_CHANS, SERVER_URL)
from err import InvalidInputError
from utils import CustomCommandFlags, CHAR_LIMIT, check_roles, send_message

class DefineModal(discord.ui.Modal):
    """
    Define Modal

    Modal for adding a new custom command

    Accessed via the `/define` slash command
    """
    def __init__(self, command_name: str):
        super().__init__(title="Define a new custom command.")
        default_title = None
        default_response = None
        default_img = None
        commands = db.get_custom_cmds()
        if command_name in commands:
            response = commands[command_name]
            default_title = response.title
            default_response = response.response
            default_img = response.img

        self.name = discord.ui.TextInput(
            label="Command Name",
            default=command_name,
            style=discord.TextStyle.short,
            required=True
        )
        self.embed_title = discord.ui.TextInput(
            label="Embed Title (Optional)",
            style=discord.TextStyle.short,
            default=default_title,
            required=False,
        )
        self.response = discord.ui.TextInput(
            label="Text Response (Needed if no image)",
            style=discord.TextStyle.long,
            max_length=CHAR_LIMIT,
            default=default_response,
            required=False,
        )
        self.img = discord.ui.TextInput(
            label="Image URL (Needed if no text)",
            style=discord.TextStyle.short,
            default=default_img,
            required=False,
        )
        self.add_item(self.name)
        self.add_item(self.embed_title)
        self.add_item(self.response)
        self.add_item(self.img)

    async def on_submit(self, interaction: discord.Interaction):
        """
        DefineModal on_submit

        Overloads discord.ui.Modal's on_submit function to handle when the modal is accepted
        """
        name = self.name.value.lower()
        title = self.embed_title.value
        response = self.response.value
        img = self.img.value
        flags = CustomCommandFlags.NONE
        is_admin = check_roles(interaction.user, ADMIN_ACCESS)

        if is_admin:
            flags |= CustomCommandFlags.ADMIN

        try:
            db.set_new_custom_cmd(name, title, response, img, flags)
        except InvalidInputError:
            await interaction.response.send_message("Custom command must have a text response and/or an image")
            return

        # Format confirmation to the user
        output_message = f"New command added! You can use it like `{CMD_PREFIX}{name}`. "

        await send_message(f"{str(interaction.user)} has changed the `{name}` command", client.log)
        await interaction.response.send_message(output_message)

def is_allowed(cmd: str, channel_id: int) -> bool:
    """
    Is Allowed

    Checks if the given custom command is allowed to be sent in the given channel
    """
    commands = db.get_custom_cmds()
    if cmd not in commands:
        return False
    response = commands[cmd]
    limited = response.flags & CustomCommandFlags.LIMITED
    if not limited:
        return True
    elif channel_id in LIMIT_CHANS:
        return False
    return True

def parse_response(command) -> discord.Embed:
    """
    Parse Response

    Return the specified response for a custom command
    """
    commands = db.get_custom_cmds()
    response = commands[command]
    embed = discord.Embed(title=response.title, description=response.response)
    if response.img is not None:
        embed.set_image(url=response.img)
    embed.set_footer(text=f"To use this command, type {CMD_PREFIX}{command}.")
    return embed

def add_alias(command: str, alias: str) -> str:
    """
    Add Alias

    Adds an alias to a pre-existing command
    """
    cmds = db.get_custom_cmds(False)
    if command not in cmds:
        return "I cannot make an alias for a command that does not exist"
    db.set_new_alias(alias, command)
    return f"`{alias}` is now an alias for `{command}`!"

async def remove_cmd(name: str, author: discord.User | discord.Member) -> str:
    """
    Remove Command

    Removes a user-defined command
    """
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

def limit_cmd(name: str) -> str:
    """
    Limit command

    Toggles limiting a command from being used in certain channels
    """
    commands = db.get_custom_cmds()
    if name in commands:
        response = commands[name]
        flag = response.flags
        # XOR to toggle that flag
        flag ^= CustomCommandFlags.LIMITED
        db.set_new_custom_cmd(name, response.title, response.response, response.img, flag)
        toggle_txt = "limited" if (flag & CustomCommandFlags.LIMITED) else "not limited"
        return f"`{name}` is now {toggle_txt} to certain channels"
    return f"`{name}` is not a known command."

def list_cmds() -> str:
    """
    List commands

    Returns a list of all user-defined commands
    """
    return f"You can see a full list of commands and their responses here: {SERVER_URL}/commands.php"
