# Governor
# Written by aquova, 2020
# https://github.com/aquova/governor

import discord
import commands
from config import DISCORD_KEY
from tracker import Tracker

client = discord.Client()
tr = Tracker()

# Dictionary of function pointers
# Maps commands (in all caps) to functions that are called by them
FUNC_DICT = {
    "!XP": commands.get_xp,
    "!LVL": commands.get_level
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
        command = message.content.upper()
        tr.user_speaks(message.author.id)

        if command in FUNC_DICT:
            output_message = FUNC_DICT[command](message)
            await message.channel.send(output_message)
    except discord.errors.HTTPException as e:
        print("HTTPException: {}".format(str(e)))
        pass

client.run(DISCORD_KEY)
