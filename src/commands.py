import discord
import db, utils
from math import floor
from config import ADMIN_ACCESS, CMD_PREFIX, RANKS, SERVER_URL
from user import parse_mention

ADMIN_HELP_MES = (
    "Define a custom message: `{prefix}define NAME [%mention%] MESSAGE`\n"
    "Edit a message spoken by the bot: `{prefix}edit MESSAGE_ID new_message`\n"
    "List custom commands: `{prefix}list`\n"
    "View your level: `{prefix}lvl`\n"
    "View available ranks: `{prefix}ranks`\n"
    "Remove a custom message: `{prefix}remove NAME`\n"
    "Speak a message as the bot: `{prefix}say CHAN_ID message`\n"
    "View your XP: `{prefix}xp`\n"
    "\nAdd a game to be announced: `{prefix}addgame game_info`\n"
    "View all games to be announced: `{prefix}getgames`\n"
    "Remove all games to be announced: `{prefix}cleargames`\n"
    "\nView this message: `{prefix}help`".format(prefix=CMD_PREFIX)
)

HELP_MES = (
    "List custom commands: `{prefix}list`\n"
    "View your level: `{prefix}lvl`\n"
    "View available ranks: `{prefix}ranks`\n"
    "View your XP: `{prefix}xp`\n"
    "\nView this message: `{prefix}help`\n".format(prefix=CMD_PREFIX)
)

"""
Print Help

Prints the help message
"""
async def print_help(message):
    # Print different message if user has advanced permissions
    roles = [x.id for x in message.author.roles]
    if ADMIN_ACCESS in roles:
        return ADMIN_HELP_MES
    else:
        return HELP_MES

"""
Show leaderboard

Posts the URL for the online leaderboard
"""
async def show_lb(message):
    return "{}/leaderboard.php".format(SERVER_URL)

"""
List ranks

Lists the available earnable rank roles, and their levels
"""
async def list_ranks(message):
    output = ""
    for rank in RANKS:
        output += "Level {}: {}\n".format(rank['level'], rank['name'])

    return output

"""
Say

Speaks a message to the specified channel as the bot
"""
@utils.requires_admin
async def say(message):
    try:
        payload = utils.remove_command(message.content)
        channel_id = utils.get_command(payload)
        channel = discord.utils.get(message.guild.channels, id=int(channel_id))
        m = utils.remove_command(payload)
        if m == "":
            return "You cannot send empty messages."

        await channel.send(m)
        return "Message sent."
    except (IndexError, ValueError):
        return "I was unable to find a channel ID in that message. `{prefix}say CHAN_ID message`".format(prefix=CMD_PREFIX)
    except AttributeError:
        return "Are you sure that was a channel ID?"
    except discord.errors.HTTPException as e:
        if e.code == 50013:
            return "You do not have permissions to post in that channel."
        else:
            return "Oh god something went wrong, everyone panic! {}".format(str(e))

"""
Edit message

Edits a message spoken by the bot, by message ID
"""
@utils.requires_admin
async def edit(message):
    try:
        payload = utils.remove_command(message.content)
        edit_id = utils.get_command(payload)
        edit_message = None
        for channel in message.guild.channels:
            try:
                if type(channel) == discord.TextChannel:
                    edit_message = await channel.fetch_message(int(edit_id))
                    break
            except discord.errors.HTTPException as e:
                if e.code == 10008:
                    pass

        if edit_message == None:
            return "I was unable to find a message with that ID."

        m = utils.remove_command(payload)
        if m == "":
            return "You cannot replace a message with nothing."

        await edit_message.edit(content=m)
        return "Message edited."
    except (IndexError, ValueError):
        return "I was unable to find a message ID in that message. `{prefix}edit MES_ID message`".format(prefix=CMD_PREFIX)
    except discord.errors.HTTPException as e:
        if e.code == 50005:
            return "You cannot edit a message from another user."
        else:
            return "Oh god something went wrong, everyone panic! {}".format(str(e))

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
    @utils.requires_admin
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
    @utils.requires_admin
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
    async def list_cmds(self, message):
        output = "```\n"
        cmds = sorted(self.cmd_dict.keys(), key=str.lower)
        for cmd in cmds:
            output += "{}, ".format(cmd)

        # Remove trailing comma
        output = output[:-2]
        output += "\n```"
        output += "\nYou can also see a full list of commands and their responses here: {}/commands.php".format(SERVER_URL)
        return output
