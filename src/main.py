# Governor
# Written by aquova, 2020
# https://github.com/aquova/governor

import discord
import db, commands, events, games, utils, xp
from config import CMD_PREFIX, DISCORD_KEY, GAME_ANNOUNCEMENT_CHANNEL, XP_OFF
from debug import Debug
from slowmode import Thermometer
from tracker import Tracker

client = discord.Client()

db.initialize()
tr = Tracker()
cc = commands.CustomCommands()
dbg = Debug()
game_timer = games.GameTimer()
thermo = Thermometer()

# Dictionary of function pointers
# Maps commands to functions that are called by them
FUNC_DICT = {
    "addgame": games.add_game,
    "addxp": tr.add_xp,
    "cleargames": games.clear_games,
    "custom": commands.print_help,
    "define": cc.define_cmd,
    "edit": commands.edit,
    "getgames": games.get_games,
    "help": commands.print_help,
    "lb": commands.show_lb,
    "level": xp.render_lvl_image,
    "list": cc.list_cmds,
    "lvl": xp.render_lvl_image,
    "ranks": commands.list_ranks,
    "remove": cc.remove_cmd,
    "say": commands.say,
    "userinfo": xp.userinfo,
    "xp": xp.get_xp,
}

# The keys in the function dict cannot be used as custom commands
cc.set_protected_keywords(list(FUNC_DICT.keys()))

"""
Update User Count

Updates the bot's 'activity' to reflect the number of users
"""
async def update_user_count(guild):
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

"""
On Guild Available

Runs when a guild (server) that the bot is connected to becomes ready
"""
@client.event
async def on_guild_available(guild):
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
async def on_member_join(user):
    await update_user_count(user.guild)

"""
On Member Remove

Runs when a member leaves the server
"""
@client.event
async def on_member_remove(user):
    await update_user_count(user.guild)

"""
On Reaction Add

Runs when a member reacts to a message with an emoji
"""
# There is no event currently going on, so this has been commented out until it is needed again
# @client.event
# async def on_reaction_add(reaction, user):
#     # TODO: This only needs to be called during an event
#     # Ideally, have some way of setting this up in config.json
#     await events.award_event_prize(reaction, user, tr)

"""
On Message

Runs when a user posts a message
"""
@client.event
async def on_message(message):
    # Ignore bots completely (including ourself)
    if message.author.bot:
        return

    # Check first if we're toggling debug mode
    # Need to do this before we discard a message
    if dbg.check_toggle(message):
        await dbg.toggle_debug(message)
        return
    elif dbg.should_ignore_message(message):
        return

    try:
        # Keep track of the user's message for dynamic slowmode
        await thermo.user_spoke(message)
        # Check if we need to congratulate a user on getting a new role
        # Don't award XP if posting in specified disabled channels
        if message.channel.id not in XP_OFF:
            lvl_up_message = await tr.give_xp(message.author)
            if lvl_up_message != None:
                await message.channel.send(lvl_up_message)

        # Check if someone is trying to use a bot command
        if message.content != "" and message.content[0] == CMD_PREFIX:
            prefix_removed = utils.strip_prefix(message.content)
            if prefix_removed == "":
                return
            command = utils.get_command(prefix_removed)

            if command in FUNC_DICT:
                # First, check if they're using a built-in command
                output_message = await FUNC_DICT[command](message)
                if output_message != None:
                    await message.channel.send(output_message)
            elif cc.command_available(command):
                # Check if they're using a user-defined command
                cmd_output = cc.parse_response(message)
                await message.channel.send(cmd_output)

    except discord.errors.HTTPException as e:
        print(f"HTTPException: {str(e)}")
        pass

client.run(DISCORD_KEY)
