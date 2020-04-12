import discord
import db, utils
from math import floor
from config import CMD_PREFIX
from user import parse_mention

HELP_MES = (
    "Define a custom message: `{prefix}define NAME [%mention%]`\n"
    "List custom commands: `{prefix}list`\n"
    "View your level: `{prefix}lvl`\n"
    "Remove a custom message: `{prefix}remove NAME`\n"
    "View your XP: `{prefix}xp`\n"
    "\nView this message: `{prefix}help`\n".format(prefix=CMD_PREFIX)
)

"""
Print Help

Prints the help message
"""
async def print_help(message):
    return HELP_MES

class CustomCommands:
    def __init__(self):
        self.cmd_dict = db.get_custom_cmds()

    """
    Set Protected Keywords

    Sets the list of protected keywords that can't be used for custom command names

    Input: keywords - Protected keywords - List(str)
    """
    def set_protected_keywords(self, keywords):
        self.keywords = keywords

    """
    Command Available

    Checks if the custom command exists

    Input: cmd - Name of command to check for - str
    """
    def command_available(self, cmd):
        return cmd in self.cmd_dict

    """
    Parse Response

    Return the specified response for a custom command

    Input: message - Discord message object
    """
    def parse_response(self, message):
        prefix_removed = utils.strip_prefix(message.content)
        command = utils.get_command(prefix_removed)
        response = self.cmd_dict[command]

        # Check if they want to embed a ping within the response
        mentioned_id = parse_mention(message)
        if mentioned_id != None:
            ping = "<@!{}>".format(mentioned_id)
        else:
            ping = ""

        response = response.replace("%mention%", ping)
        return response

    """
    Define command

    Sets a new user-defined command

    Input: message - Discord message object
    """
    async def define_cmd(self, message):
        # First remove the "define" command
        new_cmd = utils.remove_command(message.content)
        # Then parse the new command
        cmd = utils.get_command(new_cmd)
        response = utils.remove_command(new_cmd)

        if response == "":
            # Don't allow blank responses
            return "...You didn't specify what that command should do."
        elif cmd in self.keywords:
            # Don't allow users to set commands with protected keywords
            return "`{}` is already in use as a built-in function. Please choose another name.".format(cmd)

        # Set new command in cache and database
        self.cmd_dict[cmd] = response
        db.set_new_custom_cmd(cmd, response)

        # Format confirmation to the user
        output_message = "New command added! You can use it like `{}{}`. ".format(CMD_PREFIX, cmd)

        # If user allows embedding of a ping, list various ways this can be done
        if "%mention%" in response:
            author = message.author
            user_id = author.id
            user_name = "{}#{}".format(author.name, author.discriminator)
            output_message += "You can also use it as `{prefix}{cmd} {id}`, `{prefix}{cmd} {name}`, or `{prefix}{cmd} @{name}`".format(
                prefix=CMD_PREFIX, cmd=cmd, id=user_id, name=user_name)

        return output_message

    """
    Remove command

    Removes a user-defined command

    Input: message - Discord message object
    """
    async def remove_cmd(self, message):
        # First remove the "define" command
        new_cmd = utils.remove_command(message.content)
        # Then parse the command to remove
        cmd = utils.get_command(new_cmd)

        # If this command did exists, remove it from cache and database
        if self.command_available(cmd):
            del self.cmd_dict[cmd]
            db.remove_custom_cmd(cmd)

        return "`{}` removed as a custom command!".format(cmd)

    """
    List commands

    Give a list of all user-defined commands
    """
    async def list_cmds(self, _message):
        output = "```\n"
        cmds = self.cmd_dict.keys()
        for cmd in cmds:
            output += "{}, ".format(cmd)

        output += "\n```"
        return output
