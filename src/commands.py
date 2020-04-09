import discord
import db, utils
from math import floor
from config import CMD_PREFIX, XP_PER_LVL
from user import parse_mention

HELP_MES = (
    "Define a custom message: `{prefix}define NAME [%mention%]`\n"
    "List custom commands: `{prefix}list`\n"
    "View your level: `{prefix}lvl`\n"
    "View your XP: `{prefix}xp`\n"
    "\nView this message: `{prefix}help`\n".format(prefix=CMD_PREFIX)
)

def print_help(message):
    return HELP_MES

def get_xp(message):
    xp = db.fetch_user_xp(message.author.id)
    if xp == None:
        return "You have no XP :("
    else:
        return "You have {} XP".format(xp)

def get_level(message):
    xp = db.fetch_user_xp(message.author.id)
    if xp == None:
        return "You have no xp :("
    else:
        lvl = floor(xp / XP_PER_LVL)
        return "You are level {}".format(lvl)

class CustomCommands:
    def __init__(self):
        self.cmd_dict = db.get_custom_cmds()

    def set_protected_keywords(self, keywords):
        self.keywords = keywords

    def command_available(self, cmd):
        return cmd in self.cmd_dict

    def parse_response(self, message):
        prefix_removed = utils.strip_prefix(message.content)
        command = utils.get_command(prefix_removed)
        response = self.cmd_dict[command]

        mentioned_id = parse_mention(message)
        if mentioned_id != None:
            ping = "<@!{}>".format(mentioned_id)
        else:
            ping = ""

        response = response.replace("%mention%", ping)
        return response

    def define_cmd(self, message):
        # First remove the "define" command
        new_cmd = utils.remove_command(message.content)
        # Then parse the new command
        cmd = utils.get_command(new_cmd)
        response = utils.remove_command(new_cmd)
        if response == "":
            return "...You didn't specify what that command should do."
        elif cmd in self.keywords:
            return "`{}` is already in use as a built-in function. Please choose another name.".format(cmd)

        self.cmd_dict[cmd] = response
        db.set_new_custom_cmd(cmd, response)

        # Format confirmation to the user
        output_message = "New command added! You can use it like `{}{}`. ".format(CMD_PREFIX, cmd)

        if "%mention%" in response:
            author = message.author
            user_id = author.id
            user_name = "{}#{}".format(author.name, author.discriminator)
            output_message += "You can also use it as `{prefix}{cmd} {id}`, `{prefix}{cmd} {name}`, or `{prefix}{cmd} @{name}`".format(
                prefix=CMD_PREFIX, cmd=cmd, id=user_id, name=user_name)

        return output_message

    def remove_cmd(self, message):
        # First remove the "define" command
        new_cmd = utils.remove_command(message.content)
        # Then parse the command to remove
        cmd = utils.get_command(new_cmd)

        if self.command_available(cmd):
            del self.cmd_dict[cmd]
            db.remove_custom_cmd(cmd)

        return "`{}` removed as a custom command!".format(cmd)

    def list_cmds(self, _message):
        output = "```\n"
        cmds = self.cmd_dict.keys()
        for cmd in cmds:
            output += "{}\n".format(cmd)

        output += "```"
        return output
