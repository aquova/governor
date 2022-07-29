# Governor
# Written by aquova, 2020-2022
# https://github.com/aquova/governor

import re
import string

import discord
import requests
import urllib.parse

import commonbot.utils
from commonbot.debug import Debug

import db
import commands
import games
import pronouns
import xp
from client import client
from config import OWNER, DEBUG_BOT, CMD_PREFIX, DISCORD_KEY, GAME_ANNOUNCEMENT_CHANNEL, XP_OFF
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
    "lvl": xp.parse_lvl_image,
    "nobonusxp": tr.reset_bonus_xp,
    "pronouns": pronouns.post_widget,
    "postgames": game_timer.post_games,
    "ranks": commands.list_ranks,
    "remove": cc.remove_cmd,
    "say": commands.say,
    "userinfo": xp.userinfo,
    "xp": xp.get_xp,
}

# The keys in the function dict cannot be used as custom commands
cc.set_protected_keywords(list(FUNC_DICT.keys()))

# Template for SMAPI log info messages
smapi_log_message_template = string.Template(
    "**Log Info:** SMAPI $SMAPI_ver with SDV $StardewVersion on $OS, "
    "with $SMAPIMods C# mods and $ContentPacks content packs."
)

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
    print(client.user.name)
    print(client.user.id)
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
    await tr.refresh_db(guild)

    # This is 100% going to cause issues if we ever want to host on more than one server
    # TODO: If we want to fix this, make announcement channels a list in config.json, and add a server ID column to DB
    game_channel = discord.utils.get(guild.text_channels, id=GAME_ANNOUNCEMENT_CHANNEL)

    if game_channel is not None:
        print(f"Announcing games in server '{guild.name}' channel '{game_channel.name}'")
    else:
        await client.close()
        raise Exception(f"Game announcement error: couldn't find channel {GAME_ANNOUNCEMENT_CHANNEL}")

    game_timer.start(game_channel)
    thermo.start(guild)

    # Set Bouncer's status
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
    if message.channel.id not in XP_OFF:
        lvl_up_message = await tr.give_xp(message.author, message.guild)
        if lvl_up_message:
            await message.channel.send(lvl_up_message)

    for log_link in re.findall(r"https://smapi.io/log/[a-zA-Z0-9]{32}", message.content):
        log_dict = requests.get(f"http://api.pil.ninja/smapi_log/endpoint?{log_link}").json()
        if log_dict["success"]:
            windows_info = re.search(r"(Windows (?:Vista|\d+)) .+", log_dict["OS"])
            if windows_info:  # Condense OS text for Windows because it's often quite verbose.
                log_dict["OS"] = windows_info.group(1)
            await message.channel.send(smapi_log_message_template.substitute(log_dict))

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
                    await message.channel.send(output_message)
            elif cc.command_available(command):
                # Check if they're using a user-defined command
                cmd_output = cc.parse_response(message)
                await message.channel.send(cmd_output)
        except discord.errors.Forbidden as err:
            if err.code == 50013:
                print(f"I can see messages, but cannot send in #{message.channel.name}")

client.run(DISCORD_KEY)
