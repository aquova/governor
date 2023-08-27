# Governor
# Written by aquova, 2020-2023
# https://github.com/aquova/governor

import re
import urllib.parse

import discord
import requests

import commands
import commonbot.utils
import db
import games
import platforms
import xp
from client import client
from commonbot.debug import Debug
from config import (AUTO_ADD_EPIC_GAMES, CMD_PREFIX, DEBUG_BOT, DISCORD_KEY,
                    GAME_ANNOUNCEMENT_CHANNEL, OWNER, XP_OFF)
from log import parse_log
from slowmode import Thermometer
from tracker import Tracker

db.initialize()
tr = Tracker()
cc = commands.CustomCommands()
dbg = Debug(OWNER, CMD_PREFIX, DEBUG_BOT)
game_timer = games.GameTimer()
thermo = Thermometer()

# Dictionary of function pointers
# Maps commands to functions that are called by them
FUNC_DICT = {
    "addgame": games.add_game,
    "addxp": tr.add_xp,
    "bonusxp": tr.set_bonus_xp,
    "cleargames": games.clear_games,
    "custom": commands.print_help,
    "define": cc.define_cmd,
    "edit": commands.edit,
    "getgames": games.get_games,
    "help": commands.print_help,
    "info": commands.info,
    "lb": commands.show_lb,
    "level": xp.parse_lvl_image,
    "list": cc.list_cmds,
    "limit": cc.limit_cmd,
    "lvl": xp.parse_lvl_image,
    "nobonusxp": tr.reset_bonus_xp,
    "platforms": platforms.post_widget,
    "postgames": game_timer.post_games,
    "ranks": commands.list_ranks,
    "remove": cc.remove_cmd,
    "say": commands.say,
    "sync": commands.sync,
    "xp": xp.get_xp,
}

# The keys in the function dict cannot be used as custom commands
cc.set_protected_keywords(list(FUNC_DICT.keys()))

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
    client.set_channels()
    await client.setup_hook()

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
    # TODO: If we want to fix this, make announcement channels a list in config.json, and add a server ID column to DB
    game_channel = discord.utils.get(guild.text_channels, id=GAME_ANNOUNCEMENT_CHANNEL)

    if game_channel is not None:
        print(f"Announcing games in server '{guild.name}' channel '{game_channel.name}'")
    else:
        await client.close()
        raise Exception(f"Game announcement error: couldn't find channel {GAME_ANNOUNCEMENT_CHANNEL}")

    game_timer.start(game_channel, AUTO_ADD_EPIC_GAMES and not dbg.is_debug_bot())
    thermo.start(guild)
    tr.start(guild)

    # Set Bouncer's status
    await update_user_count(guild)
    await client.sync_guild(guild)


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
    tr.remove_from_cache(user.id)
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

    # For now, completely ignore DMs
    if isinstance(message.channel, discord.channel.DMChannel):
        return

    # Check first if we're toggling debug mode
    # Need to do this before we discard a message
    if dbg.check_toggle(message):
        await dbg.toggle_debug(message)
        return
    elif dbg.should_ignore_message(message):
        return

    # Keep track of the user's message for dynamic slowmode
    await thermo.user_spoke(message)
    # Check if we need to congratulate a user on getting a new role
    # Don't award XP if posting in specified disabled channels
    if message.channel.id not in XP_OFF and message.guild is not None:
        lvl_up_message = await tr.give_xp(message.author)
        if lvl_up_message:
            await message.channel.send(lvl_up_message)

    for log_link in re.findall(r"https://smapi.io/log/[a-zA-Z0-9]{32}", message.content):
        log_info = parse_log(log_link)
        await message.channel.send(log_info)

    for community_wiki_link in re.findall(r"https://stardewcommunitywiki\.com/[a-zA-Z0-9_/:\-%]*", message.content):
        new_wiki ="https://stardewvalleywiki.com"

        link_path = urllib.parse.urlparse(community_wiki_link).path
        new_url = urllib.parse.urljoin(new_wiki, link_path)
        await message.channel.send(f"I notice you're linking to the old wiki, that wiki has been in a read-only state for several months. Here are the links to that page on the new wiki: {new_url}")


    for attachment in message.attachments:
        if attachment.filename == "SMAPI-latest.txt" or attachment.filename == "SMAPI-crash.txt":
            r = requests.get(attachment.url)
            log = urllib.parse.quote(r.text)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }

            s = requests.post('https://smapi.io/log/', data="input={0}".format(log), headers=headers)
            logurl = s.text.split('</strong> <code>')[1].split('</code>')[0]
            await message.channel.send("Log found, uploaded to: " + logurl)


    # Check if someone is trying to use a bot command
    if message.content != "" and message.content[0] == CMD_PREFIX:
        prefix_removed = commonbot.utils.strip_prefix(message.content, CMD_PREFIX)
        if prefix_removed == "":
            return
        command = commonbot.utils.get_first_word(prefix_removed).lower()

        try:
            if command in FUNC_DICT:
                # First, check if they're using a built-in command
                output_message = await FUNC_DICT[command](message)
                if output_message:
                    await commonbot.utils.send_message(output_message, message.channel)
            elif cc.is_allowed(command, message.channel.id):
                # Check if they're using a user-defined command
                cmd_output = cc.parse_response(message)
                await message.channel.send(cmd_output)
        except discord.errors.Forbidden as err:
            if err.code == 50013:
                print(f"I can see messages, but cannot send in #{message.channel.name}")

client.run(DISCORD_KEY)
