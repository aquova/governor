# Governor
# Written by aquova, 2020
# https://github.com/aquova/governor

import discord, json

# Read values from config file
with open('private/config.json') as config_file:
    cfg = json.load(config_file)

discordKey = cfg['discord']
client = discord.Client()

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
        chan = message.channel
        await chan.send(message.content)
    except discord.errors.HTTPException as e:
        print("HTTPException: {}".format(str(e)))
        pass

client.run(discordKey)
