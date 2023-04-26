import discord

import commonbot.utils
from commonbot.user import UserLookup

import db
from client import client
from config import ADMIN_ACCESS, CMD_PREFIX, RANKS, SERVER_URL, LVL_CHANS, NO_SLOWMODE, XP_OFF, LOG_CHAN, LIMIT_CHANS
from utils import requires_admin, requires_define, CustomCommandFlags

ul = UserLookup()

ADMIN_HELP_MES = (
    f"## XP\n"
    f"View your XP: `{CMD_PREFIX}xp`\n"
    f"View your level: `{CMD_PREFIX}lvl`\n"
    f"Set XP to be x2: `{CMD_PREFIX}bonusxp`\n"
    f"Reset XP multiplier: `{CMD_PREFIX}nobonusxp`\n"
    f"Give XP to a user: `{CMD_PREFIX}addxp USER XP` (Can be negative)\n"
    f"## Custom Commands\n"
    f"Define a custom message: `{CMD_PREFIX}define NAME [%mention%] MESSAGE`\n"
    f"List custom commands: `{CMD_PREFIX}list`\n"
    f"Remove a custom message: `{CMD_PREFIX}remove NAME`\n"
    f"Limit a custom message: `{CMD_PREFIX}limit NAME`\n"
    f"## Server Control\n"
    f"Speak a message as the bot: `{CMD_PREFIX}say CHAN_ID message`. If you want to send images they must be attachments *not URLs*.\n"
    f"Edit a message spoken by the bot: `{CMD_PREFIX}edit MESSAGE_ID new_message`\n"
    f"Display info on a user: `{CMD_PREFIX}userinfo [USER]`\n"
    f"Display info on bot settings: `{CMD_PREFIX}info`\n"
    f"View available ranks: `{CMD_PREFIX}ranks`\n"
    f"## Interactive Commands\n"
    f"Sync slash commands to the server: `{CMD_PREFIX}sync`\n"
    f"Post the platform selection menu (rarely do this): `{CMD_PREFIX}platforms CHAN_ID`\n"
    f"Post the pronoun selection menu (rarely do this): `{CMD_PREFIX}pronouns CHAN_ID`\n"
    f"## Announce Games\n"
    f"Add a game to be announced: `{CMD_PREFIX}addgame URL`\n"
    f"View all games to be announced: `{CMD_PREFIX}getgames`\n"
    f"Post games immediately: `{CMD_PREFIX}postgames`\n"
    f"Remove all games to be announced: `{CMD_PREFIX}cleargames`\n"
    f"\n"
    f"View this message: `{CMD_PREFIX}help`"
)

HELP_MES = (
    f"## XP"
    f"View your XP: `{CMD_PREFIX}xp`\n"
    f"View your level: `{CMD_PREFIX}lvl`\n"
    f"\n"
    f"## Custom Commands"
    f"List custom commands: `{CMD_PREFIX}list`\n"
    f"Define a custom command: `{CMD_PREFIX}define NAME [%mention%] MESSAGE` (only available to certain roles)\n"
    f"View available ranks: `{CMD_PREFIX}ranks`\n"
    f"Display info on a user: `{CMD_PREFIX}userinfo [USER]`\n"
    f"\n"
    f"View this message: `{CMD_PREFIX}help`\n"
)

"""
Print Help

Prints the help message
"""
async def print_help(message: discord.Message) -> str:
    # Print different message if user has advanced permissions
    try:
        if commonbot.utils.check_roles(message.author, ADMIN_ACCESS):
            return ADMIN_HELP_MES
        return HELP_MES
    except AttributeError:
        return HELP_MES

"""
Show leaderboard

Posts the URL for the online leaderboard
"""
async def show_lb(_) -> str:
    return f"{SERVER_URL}/leaderboard.php"

"""
List ranks

Lists the available earnable rank roles, and their levels
"""
async def list_ranks(_) -> str:
    output = ""
    for rank in RANKS:
        output += f"Level {rank['level']}: {rank['name']}\n"
    return output

"""
Say

Speaks a message to the specified channel as the bot
"""
@requires_admin
async def say(message: discord.Message) -> str:
    try:
        payload = commonbot.utils.strip_words(message.content, 1)
        channel_id = commonbot.utils.get_first_word(payload)
        channel = discord.utils.get(message.guild.channels, id=int(channel_id))
        output = commonbot.utils.strip_words(payload, 1)
        if output == "" and len(message.attachments) == 0:
            return "You cannot send empty messages."

        for item in message.attachments:
            my_file = await item.to_file()
            await channel.send(file=my_file)

        if output != "":
            await channel.send(output, allowed_mentions=discord.AllowedMentions.none())

        return "Message sent."
    except (IndexError, ValueError):
        return f"I was unable to find a channel ID in that message. `{CMD_PREFIX}say CHAN_ID message`"
    except AttributeError:
        return "Are you sure that was a channel ID?"
    except discord.errors.HTTPException as err:
        if err.code == 50013:
            return "You do not have permissions to post in that channel."
        else:
            return f"Oh god something went wrong, everyone panic! {str(err)}"

"""
Edit message

Edits a message spoken by the bot, by message ID
"""
@requires_admin
async def edit(message: discord.Message) -> str:
    try:
        payload = commonbot.utils.strip_words(message.content, 1)
        edit_id = commonbot.utils.get_first_word(payload)
        edit_message = None
        for channel in message.guild.channels:
            try:
                if isinstance(channel, discord.TextChannel):
                    edit_message = await channel.fetch_message(int(edit_id))
                    break
            except discord.errors.HTTPException as err:
                if err.code == 10008:
                    pass

        if not edit_message:
            return "I was unable to find a message with that ID."

        output = commonbot.utils.strip_words(payload, 1)
        if output == "":
            return "You cannot replace a message with nothing."

        await edit_message.edit(content=output)
        return "Message edited."
    except (IndexError, ValueError):
        return "I was unable to find a message ID in that message. `{CMD_PREFIX}edit MES_ID message`"
    except discord.errors.HTTPException as err:
        if err.code == 50005:
            return "You cannot edit a message from another user."
        else:
            return f"Oh god something went wrong, everyone panic! {str(err)}"

@requires_admin
async def info(_) -> str:
    lvl_c = ", ".join([f"<#{x}>" for x in LVL_CHANS])
    slow_c = ", ".join([f"<#{x}>" for x in NO_SLOWMODE])
    xp_c = ", ".join([f"<#{x}>" for x in XP_OFF])
    limit_c = ", ".join([f"<#{x}>" for x in LIMIT_CHANS])
    mes = (
        f"The `{CMD_PREFIX}lvl` command is only allowed in {lvl_c}\n"
        f"Dynamic slowmode is disabled in {slow_c}\n"
        f"Users do not gain XP in {xp_c}\n"
        f"Commands can be disabled in {limit_c}\n"
    )
    return mes

@requires_admin
async def sync(message: discord.Message) -> str:
    import context
    await client.sync_guild(message.guild)
    return "Commands synced"

class CustomCommands:
    def __init__(self):
        self.keywords = None
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
        # If user allows embedding of a ping, list various ways this can be done
        if "%mention%" in response:
            user_id = author.id
            output_message += f"You can also use it as `{CMD_PREFIX}{cmd} {user_id}`, `{CMD_PREFIX}{cmd} {str(author)}`, or `{CMD_PREFIX}{cmd} @{str(author)}`"

        log_msg = ""
        log_chan = client.get_channel(LOG_CHAN)
        if old_response:
            log_msg = f"{str(author)} has changed the command `{cmd}` from `{old_response}` to `{response}`"
        else:
            log_msg = f"{str(author)} has added the `{cmd}` command - `{response}`"

        await log_chan.send(log_msg)

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

            log_chan = client.get_channel(LOG_CHAN)
            log_msg = f"{str(message.author)} has removed the `{cmd}` command. It used to say `{old_msg}`."
            await log_chan.send(log_msg)

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
