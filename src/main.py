# Governor
# Written by aquova, 2020
# https://github.com/aquova/governor

import discord
import db, commands, utils, xp, games
from config import CMD_PREFIX, DISCORD_KEY, GAME_ANNOUNCEMENT_CHANNEL
from debug import Debug
from tracker import Tracker

client = discord.Client()

db.initialize()
tr = Tracker()
cc = commands.CustomCommands()
dbg = Debug()
game_timer = games.GameTimer()

# Dictionary of function pointers
# Maps commands (in all caps) to functions that are called by them
FUNC_DICT = {
    "custom": commands.print_help,
    "define": cc.define_cmd,
    "debug": dbg.toggle_debug,
    "edit": commands.edit,
    "help": commands.print_help,
    "lb": commands.show_lb,
    "level": xp.render_lvl_image,
    "list": cc.list_cmds,
    "lvl": xp.render_lvl_image,
    "ranks": commands.list_ranks,
    "remove": cc.remove_cmd,
    "say": commands.say,
    "xp": xp.get_xp,
    "addgame": games.add_game,
    "cleargames": games.clear_games,
    "getgames": games.get_games,
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
On Guild Available

Runs when a guild (server) that the bot is connected to becomes ready
"""
@client.event
async def on_guild_available(guild):
    # This is 100% going to cause issues if we ever want to host on more than one server
    # TODO: If we want to fix this, make announcement channels a list in config.json, and add a server ID column to DB
    game_channel = discord.utils.get(guild.text_channels, id=GAME_ANNOUNCEMENT_CHANNEL)

    if game_channel is not None:
        print(f"Announcing games in server '{guild.name}' channel '{game_channel.name}'")
    else:
        await client.close()
        raise Exception(f"Game announcement error: couldn't find channel {GAME_ANNOUNCEMENT_CHANNEL}")

    game_timer.start(game_channel)

"""
On Message

Runs when a user posts a message
"""
@client.event
async def on_message(message):
    # Ignore bots completely (including ourself)
    if message.author.bot:
        return

    if dbg.should_ignore_message(message):
        return

    try:
        # Check if we need to congratulate a user on getting a new role
        lvl_up_message = await tr.user_speaks(message.author)
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
        print("HTTPException: {}".format(str(e)))
        pass

client.run(DISCORD_KEY)
