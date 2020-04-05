# Governor
# Written by aquova, 2020
# https://github.com/aquova/governor

import discord
import commands, utils
from config import DISCORD_KEY, CMD_PREFIX
from tracker import Tracker

client = discord.Client()
tr = Tracker()

# Dictionary of function pointers
# Maps commands (in all caps) to functions that are called by them
FUNC_DICT = {
    "DEFINE": commands.define_cmd,
    "LIST": commands.list_cmds,
    "LVL": commands.get_level,
    "XP": commands.get_xp,
}

"""
On Ready

Runs when Discord bot is first brought online
"""
@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)

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
        lvl_up_message = await tr.user_speaks(message.author)
        if lvl_up_message != None:
            await message.channel.send(lvl_up_message)

        if message.content[0] == CMD_PREFIX:
            phrase = utils.strip_prefix(message.content)
            command = utils.get_command(phrase).upper()
            if command in FUNC_DICT:
                output_message = FUNC_DICT[command](message)
                await message.channel.send(output_message)
            elif command in commands.get_custom_commands():
                cmd_output = commands.get_custom_commands()[command]
                await message.channel.send(cmd_output)

    except discord.errors.HTTPException as e:
        print("HTTPException: {}".format(str(e)))
        pass
    except Exception as e:
        print(str(e))

client.run(DISCORD_KEY)
