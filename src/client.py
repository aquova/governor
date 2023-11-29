from typing import cast

import discord
from discord.ext import commands
from commonbot.debug import Debug
from commonbot.timestamp import calculate_timestamps

from config import CMD_PREFIX, DEBUG_BOT, LOG_CHAN, OWNER
from games import GameTimer
from slowmode import Thermometer
from tracker import Tracker
from platforms import PlatformWidget
import utils, xp

class DiscordClient(commands.Bot):
    def __init__(self):
        my_intents = discord.Intents.all()
        super().__init__(command_prefix=CMD_PREFIX, intents=my_intents)
        self.dbg = Debug(OWNER, CMD_PREFIX, DEBUG_BOT)
        self.game_timer = GameTimer(self.dbg.is_debug_bot())
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

@client.tree.command(name="bonusxp", description="Enable/Disable XP multiplier")
@discord.app_commands.describe(enabled="y/N")
async def bonus_xp_context(interaction: discord.Interaction, enabled: str):
    set_bonus = enabled.upper() == "Y"
    response = await client.tracker.set_bonus_xp(set_bonus)
    await interaction.response.send_message(response, ephemeral=True)

@client.tree.command(name="level", description="View your customized level image")
async def lvl_context(interaction: discord.Interaction):
    filename = await xp.render_lvl_image(interaction.user)
    if filename:
        with open(filename, 'rb') as my_file:
            discord_file = discord.File(my_file)
            await interaction.response.send_message(file=discord_file)
    else:
        await interaction.response.send_message("Error: Something went wrong. Please try again.", ephemeral=True)

@client.tree.command(name="leaderboard", description="Get the URL for the online leaderboard")
async def lb_context(interaction: discord.Interaction):
    url = utils.show_lb()
    await interaction.response.send_message(url, ephemeral=True)

@client.tree.command(name="ranks", description="List the earnable ranks for the server")
async def ranks_context(interaction: discord.Interaction):
    ranks = utils.list_ranks()
    await interaction.response.send_message(ranks, ephemeral=True)

@client.tree.command(name="timestamp", description="Convert a time into a universal timestamp")
@discord.app_commands.describe(date="YYYY/MM/DD", time="HH:MM", tz="Either UTC±X or common name (ex. CST)")
async def timestamp(interaction: discord.Interaction, date: str, time: str, tz: str):
    try:
        message = calculate_timestamps(date, time, tz)
        await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        await interaction.response.send_message("Error: One of the entries has an invalid format.", ephemeral=True)

### Member Context Commands ###
@client.tree.context_menu(name="Level")
async def lvl_member(interaction: discord.Interaction, user: discord.Member):
    filename = await xp.render_lvl_image(user)
    if filename:
        with open(filename, 'rb') as my_file:
            discord_file = discord.File(my_file)
            await interaction.response.send_message(file=discord_file)
    else:
        await interaction.response.send_message("Error: Something went wrong. Please try again.", ephemeral=True)

@client.tree.context_menu(name="User Info")
async def userinfo_context(interaction: discord.Interaction, user: discord.Member):
    if isinstance(interaction.user, discord.User):
        return
    embed = xp.create_user_info_embed(user)
    await interaction.response.send_message(embed=embed, ephemeral=True)

