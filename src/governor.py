# Governor
# Written by aquova, 2020
# https://github.com/aquova/governor

import discord
import commands, utils
from config import DISCORD_KEY, CMD_PREFIX
from tracker import Tracker

client = discord.Client()
tr = Tracker()
cc = commands.CustomCommands()

# Dictionary of function pointers
# Maps commands (in all caps) to functions that are called by them
FUNC_DICT = {
    "define": cc.define_cmd,
    "help": commands.print_help,
    "list": cc.list_cmds,
    "lvl": commands.get_level,
    "remove": cc.remove_cmd,
    "xp": commands.get_xp,
}

# The keys in the function dict cannot be used as custom commands
cc.set_protected_keywords(FUNC_DICT.keys())

"""
On Ready

Runs when Discord bot is first brought online
"""
@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)

    # Currently, this will only be one guild, but this is here for future proofing
    for guild in client.guilds:
        await tr.refresh_db(guild)

"""
On Message

Runs when a user posts a message
"""
@client.event
async def on_message(message):
    # Don't react to your message
    if message.author.id == client.user.id:
        return

    try:
        # Check if we need to congratulate a user on getting a new role
        lvl_up_message = await tr.user_speaks(message.author)
        if lvl_up_message != None:
            await message.channel.send(lvl_up_message)

        # Check if someone is trying to use a bot command
        if message.content != "" and message.content[0] == CMD_PREFIX:
            prefix_removed = utils.strip_prefix(message.content)
            command = utils.get_command(prefix_removed)

            if command in FUNC_DICT:
                # First, check if they're using a built-in command
                output_message = FUNC_DICT[command](message)
                await message.channel.send(output_message)
            elif cc.command_available(command):
                # Check if they're using a user-defined command
                cmd_output = cc.parse_response(message)
                await message.channel.send(cmd_output)

    except discord.errors.HTTPException as e:
        print("HTTPException: {}".format(str(e)))
        pass

client.run(DISCORD_KEY)
