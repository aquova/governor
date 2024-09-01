from typing import cast

import discord
from discord.ext import commands

from config import CMD_PREFIX, LOG_CHAN, RESOLVED_TAG, OPEN_TAGS
from platforms import PlatformWidget
from slowmode import Thermometer
from timestamp import calculate_timestamps
from tracker import Tracker
import custom, db, games, say, utils, xp

HELP_MESSAGE = (
    "# Governor Slash Command Reference\n"
    "`/help` - Print this message\n"
    "## User Levels\n"
    "`/level` - Render a user's level image\n"
    "`/lvl` - Render your level image\n"
    "`/xp` - Gets the user's XP\n"
    "`/addxp` - Award XP to a user\n"
    "`/bonusxp` - Toggle XP multiplier\n"
    "`/ranks` - List earnable ranks\n"
    "`/lb` - Get the URL for the leaderboard\n"
    "## Game Giveaways\n"
    "`/addgame` - Add giveway URL to be posted\n"
    "`/getgames` - Get the list of giveaways to be posted\n"
    "`/cleargames` - Clear games giveaway queue\n"
    "`/postgames` - Immediately post the giveaway queue\n"
    "## Custom Commands\n"
    "`/define` - Add a new custom command\n"
    "`/alias` - Add an alias to an existing custom command\n"
    "`/remove` - Remove a custom command or alias\n"
    "`/list` - List the custom commands\n"
    "`/limit` - Limit usage of a custom command\n"
    "## Misc.\n"
    "`/say` - Say a message as the bot\n"
    "`/edit` - Edit a message sent by the bot\n"
    "`/postplatforms` - Post the platform role selection buttons\n"
    "`/info` - Print info about bot settings\n"
    "`/timestamp` - Convert a time into a Discord timestamp\n"
)

class DiscordClient(commands.Bot):
    def __init__(self):
        my_intents = discord.Intents.all()
        super().__init__(command_prefix=CMD_PREFIX, intents=my_intents)
        db.initialize()

        self.game_timer = games.GameTimer()
        self.thermometer = Thermometer()
        self.tracker = Tracker()

    async def setup(self, guild: discord.Guild):
        self.log = cast(discord.TextChannel, self.get_channel(LOG_CHAN))

        try:
            self.game_timer.setup(guild)
        except Exception as e:
            await self.close()
            raise e
        self.thermometer.setup(guild)
        self.tracker.setup(guild)

        await self.add_cog(self.game_timer)
        await self.add_cog(self.thermometer)
        await self.add_cog(self.tracker)
        self.add_view(PlatformWidget())

    async def sync_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

client = DiscordClient()

### Slash Commands ###
# Keep in alphabetical order

@client.tree.command(name="addgame", description="Add a game giveaway URL to be posted")
@discord.app_commands.describe(url="URL")
async def addgame_context(interaction: discord.Interaction, url: str):
    response = games.add_game(url)
    await interaction.response.send_message(response)

@client.tree.command(name="addxp", description="Award XP to a user")
@discord.app_commands.describe(user="User", xp="XP points to add")
async def addxp_context(interaction: discord.Interaction, user: discord.Member, xp: int):
    response = await client.tracker.add_xp(user, xp)
    await interaction.response.send_message(response)

@client.tree.command(name="alias", description="Add an alias to an existing command")
@discord.app_commands.describe(command="Command Name", alias="Alias")
async def alias_context(interaction: discord.Interaction, command: str, alias: str):
    response = custom.add_alias(command, alias)
    await interaction.response.send_message(response)

@client.tree.command(name="bonusxp", description="Enable/Disable XP multiplier")
@discord.app_commands.describe(enabled="y/N")
async def bonus_xp_context(interaction: discord.Interaction, enabled: str):
    set_bonus = enabled.upper() == "Y"
    response = await client.tracker.set_bonus_xp(set_bonus)
    await interaction.response.send_message(response)

@client.tree.command(name="cleargames", description="Clears the games giveaway queue")
async def cleargames_context(interaction: discord.Interaction):
    response = games.clear_games()
    await interaction.response.send_message(response)

@client.tree.command(name="define", description="Open a window to add a new custom command")
@discord.app_commands.describe(command="Command Name")
async def define_context(interaction: discord.Interaction, command: str):
    await interaction.response.send_modal(custom.DefineModal(command))

@client.tree.command(name="edit", description="Edit a message sent by the bot")
@discord.app_commands.describe(channel="Channel message is in", message_id="Message ID")
async def edit_context(interaction: discord.Interaction, channel: discord.TextChannel, message_id: str):
    await interaction.response.send_modal(say.EditModal(channel, message_id))

@client.tree.command(name="getgames", description="Get the list of giveaways to be announced")
async def getgames_context(interaction: discord.Interaction):
    response = games.get_games()
    await interaction.response.send_message(response)

@client.tree.command(name="help", description="Print slash command help message")
async def help_context(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_MESSAGE)

@client.tree.command(name="info", description="Print info about bot settings")
async def info_context(interaction: discord.Interaction):
    response = utils.get_bot_info()
    await interaction.response.send_message(response)

@client.tree.command(name="lb", description="Get the URL for the online leaderboard")
async def lb_context(interaction: discord.Interaction):
    url = utils.show_lb()
    await interaction.response.send_message(url, ephemeral=True)

@client.tree.command(name="level", description="View a customized level image")
@discord.app_commands.describe(user="User")
async def level_context(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()
    filename = await xp.render_lvl_image(user)
    if filename:
        with open(filename, 'rb') as my_file:
            discord_file = discord.File(my_file)
            await interaction.followup.send(file=discord_file)
            return
    await interaction.followup.send("Error: Something went wrong. Please try again.", ephemeral=True)

@client.tree.command(name="lvl", description="View your level image")
async def lvl_context(interaction: discord.Interaction):
    await interaction.response.defer()
    filename = await xp.render_lvl_image(interaction.user)
    if filename:
        with open(filename, 'rb') as my_file:
            discord_file = discord.File(my_file)
            await interaction.followup.send(file=discord_file)
            return
    await interaction.followup.send("Error: Something went wrong. Please try again.", ephemeral=True)

@client.tree.command(name="limit", description="Limit usage of a command in certain channels")
@discord.app_commands.describe(name="Command Name")
async def limit_context(interaction: discord.Interaction, name: str):
    response = custom.limit_cmd(name)
    await interaction.response.send_message(response)

@client.tree.command(name="list", description="List the custom commands")
async def list_context(interaction: discord.Interaction):
    response = custom.list_cmds()
    await interaction.response.send_message(response, ephemeral=True)

@client.tree.command(name="postgames", description="Immediately post the list of game giveaways, if any")
async def postgames_context(interaction: discord.Interaction):
    response = await client.game_timer.post_games()
    await interaction.response.send_message(response)

@client.tree.command(name="postplatforms", description="Post the platform selection buttons")
@discord.app_commands.describe(channel="Channel to post in")
async def postplatforms_context(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.send("Assign yourself any of the platforms you use!", view=PlatformWidget())
    await interaction.response.send_message("Widget posted!")

@client.tree.command(name="ranks", description="List the earnable ranks for the server")
async def ranks_context(interaction: discord.Interaction):
    ranks = utils.list_ranks()
    await interaction.response.send_message(ranks, ephemeral=True)

@client.tree.command(name="remove", description="Remove a custom command or alias")
@discord.app_commands.describe(name="Command Name")
async def remove_context(interaction: discord.Interaction, name: str):
    response = await custom.remove_cmd(name, interaction.user)
    await interaction.response.send_message(response)

@client.tree.command(name="resolve", description="Mark this thread as resolved")
async def resolve_context(interaction: discord.Interaction):
    if interaction.channel is not None and interaction.channel.type == discord.ChannelType.public_thread:
        resolve_tag = interaction.channel.parent.get_tag(RESOLVED_TAG)
        tags = []
        if resolve_tag is not None:
            tags.append(resolve_tag)
        for tag in interaction.channel.applied_tags:
            if tag is not None and tag.id not in OPEN_TAGS:
                tags.append(tag)
        await interaction.channel.edit(locked=True, applied_tags=tags)
        await interaction.response.send_message("Thread resolved!", ephemeral=True)

@client.tree.command(name="say", description="Open a window to post a message as the bot")
@discord.app_commands.describe(channel="Channel to post in")
async def say_context(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.send_modal(say.SayModal(channel))

@client.tree.command(name="timestamp", description="Convert a time into a universal timestamp")
@discord.app_commands.describe(date="YYYY/MM/DD", time="HH:MM", tz="Either UTC±X or common name (ex. CST)")
async def timestamp(interaction: discord.Interaction, date: str, time: str, tz: str):
    try:
        message = calculate_timestamps(date, time, tz)
        await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        await interaction.response.send_message("Error: One of the entries has an invalid format.", ephemeral=True)

@client.tree.command(name="userinfo", description="Get information about a user's profile")
@discord.app_commands.describe(user="User")
async def userinfo_slash(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()
    embed = xp.create_user_info_embed(user)
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="xp", description="Gets the user's XP value")
@discord.app_commands.describe(user="User")
async def getxp_context(interaction: discord.Interaction, user: discord.Member):
    response = xp.get_xp(user)
    await interaction.response.send_message(response, ephemeral=True)

### Member Context Commands ###
@client.tree.context_menu(name="Level")
async def lvl_member(interaction: discord.Interaction, user: discord.Member):
    filename = await xp.render_lvl_image(user)
    if filename:
        with open(filename, 'rb') as my_file:
            discord_file = discord.File(my_file)
            await interaction.response.send_message(file=discord_file)
            return
    await interaction.response.send_message("Error: Something went wrong. Please try again.", ephemeral=True)

@client.tree.context_menu(name="User Info")
async def userinfo_context(interaction: discord.Interaction, user: discord.Member):
    if isinstance(interaction.user, discord.User):
        return
    embed = xp.create_user_info_embed(user)
    await interaction.response.send_message(embed=embed, ephemeral=True)

