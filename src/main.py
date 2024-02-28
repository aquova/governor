# Governor
# Written by aquova, 2020-2024
# https://github.com/aquova/governor

import discord

import custom, log
from client import client
from config import CMD_PREFIX, DISCORD_KEY, XP_OFF

"""
Update User Count

Updates the bot's 'activity' to reflect the number of users
"""
async def update_user_count(guild: discord.Guild):
    activity_mes = f"{guild.member_count} members!"
    activity_object = discord.Activity(name=activity_mes, type=discord.ActivityType.watching)
    await client.change_presence(activity=activity_object)

"""
On Ready

Runs when Discord bot is first brought online
"""
@client.event
async def on_ready():
    print("Logged in as:")
    if client.user:
        print(client.user.name)
        print(client.user.id)

"""
On Thread Create

Occurs when a new thread is created in the server
"""
@client.event
async def on_thread_create(thread: discord.Thread):
    await thread.join()

"""
On Guild Available

Runs when a guild (server) that the bot is connected to becomes ready
"""
@client.event
async def on_guild_available(guild: discord.Guild):
    # This is 100% going to cause issues if we ever want to host on more than one server
    await client.setup(guild)
    await client.sync_guild(guild)

    await update_user_count(guild)

"""
On Member Join

Runs when a user joins the server
"""
@client.event
async def on_member_join(user: discord.Member):
    await update_user_count(user.guild)

"""
On Member Remove

Runs when a member leaves the server
"""
@client.event
async def on_member_remove(user: discord.Member):
    client.tracker.remove_from_cache(user.id)
    await update_user_count(user.guild)

"""
On Message

Runs when a user posts a message
"""
@client.event
async def on_message(message: discord.Message):
    # Ignore bots completely (including ourself)
    if message.author.bot:
        return

    # Completely ignore DMs
    if isinstance(message.channel, discord.channel.DMChannel):
        return

    # Keep track of the user's message for dynamic slowmode
    await client.thermometer.user_spoke(message)
    # Check if we need to congratulate a user on getting a new role
    # Don't award XP if posting in specified disabled channels
    if message.channel.id not in XP_OFF and message.guild is not None:
        lvl_up_message = await client.tracker.give_xp(message.author)
        if lvl_up_message:
            await message.channel.send(lvl_up_message)

    # Check if the user has uploaded SMAPI diagnostic info
    await log.check_log_link(message)
    await log.check_attachments(message)

    # Check if someone is trying to use a custom command
    if message.content != "" and message.content[0] == CMD_PREFIX:
        raw_command = message.content[1:]
        command = raw_command.split(" ")[0].lower()
        if custom.is_allowed(command, message.channel.id):
            response = custom.parse_response(command)
            await message.channel.send(response)

client.run(DISCORD_KEY)
