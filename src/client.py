from math import floor
from typing import cast

from bs4 import BeautifulSoup, Tag
import discord, requests
from discord.ext import commands
from commonbot.timestamp import calculate_timestamps

import db, xp
from config import CMD_PREFIX, LOG_CHAN, MODDER_ROLE, MODDER_URL, RANKS, SERVER_URL, XP_PER_LVL
from slowmode import Thermometer
from tracker import Tracker
from platforms import PlatformWidget

class DiscordClient(commands.Bot):
    def __init__(self):
        my_intents = discord.Intents.all()
        super().__init__(command_prefix=CMD_PREFIX, intents=my_intents)

    async def setup(self, guild: discord.Guild):
        self.log = cast(discord.TextChannel, self.get_channel(LOG_CHAN))
        self.thermometer = Thermometer(guild)
        self.tracker = Tracker(guild)
        await self.add_cog(self.thermometer)
        await self.add_cog(self.tracker)
        self.add_view(PlatformWidget())

    async def sync_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

client = DiscordClient()

"""
Show leaderboard

Posts the URL for the online leaderboard
"""
async def show_lb(_) -> str:
    return f"{SERVER_URL}/leaderboard.php"

"""
List ranks

Lists the available earnable rank roles, and their levels
"""
async def list_ranks(_) -> str:
    output = ""
    for rank in RANKS:
        output += f"Level {rank['level']}: {rank['name']}\n"
    return output

def find_modder_info(uid: str) -> list[tuple[str, str]]:
    r = requests.get(MODDER_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    soup.encode("utf-8")
    info = soup.find("tr", {"data-discord-id": uid})
    mods = []
    if isinstance(info, Tag):
        rows = info.find_all("td")
        mod_links = rows[1].find_all("a") # This will break if the table adds another column
        mods = [(a.decode_contents(), a['href']) for a in mod_links]
    return mods

@client.tree.command(name="leaderboard", description="Get the URL for the online leaderboard")
async def lb_context(interaction: discord.Interaction):
    url = await show_lb(None)
    await interaction.response.send_message(url, ephemeral=True)

@client.tree.command(name="ranks", description="List the earnable ranks for the server")
async def ranks_context(interaction: discord.Interaction):
    ranks = await list_ranks(None)
    await interaction.response.send_message(ranks, ephemeral=True)

@client.tree.command(name="level", description="View your customized level image")
async def lvl_context(interaction: discord.Interaction):
    filename = await xp.render_lvl_image(interaction.user)
    if filename:
        with open(filename, 'rb') as my_file:
            discord_file = discord.File(my_file)
            await interaction.response.send_message(file=discord_file, ephemeral=True)

@client.tree.command(name="timestamp", description="Convert a time into a universal timestamp")
@discord.app_commands.describe(date="YYYY/MM/DD", time="HH:MM", tz="Either UTC±X or common name (ex. CST)")
async def timestamp(interaction: discord.Interaction, date: str, time: str, tz: str):
    try:
        message = calculate_timestamps(date, time, tz)
        await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        await interaction.response.send_message("Error: One of the entries has an invalid format.", ephemeral=True)

@client.tree.context_menu(name="User Info")
async def userinfo_context(interaction: discord.Interaction, user: discord.Member):
    if isinstance(interaction.user, discord.User):
        return
    username = str(user)
    if user.nick is not None:
        username += f" aka {user.nick}"
    embed = discord.Embed(title=username, type="rich", color=user.color)
    embed.description = str(user.id)
    embed.set_thumbnail(url=user.display_avatar.url)

    xp = db.fetch_user_xp(user.id)
    lvl = floor(xp / XP_PER_LVL)
    monthly = db.fetch_user_monthly_xp(user.id)
    embed.add_field(name="Level", value=lvl)
    embed.add_field(name="Total XP", value=xp)
    embed.add_field(name="Monthly XP", value=monthly)

    # Only bother accessing and parsing the wiki if they have the modder role
    if MODDER_ROLE in [x.id for x in user.roles]:
        mod_info = find_modder_info(str(user.id))
        for mod in mod_info:
            embed.add_field(name=mod[0], value=mod[1], inline=False)

    # The first role is always @everyone, so omit it
    roles = [x.name for x in user.roles[1:]]
    role_str = ", ".join(roles)
    # Discord will throw an error if we try to have a field with an empty string
    if len(roles) > 0:
        embed.add_field(name="Roles", value=role_str, inline=False)

    # https://strftime.org/ is great if you ever want to change this, FYI
    create_time = user.created_at.strftime("%c")
    embed.add_field(name="Created", value=create_time)

    if user.joined_at is not None:
        join_time = user.joined_at.strftime("%c")
        embed.add_field(name="Joined", value=join_time)

    await interaction.response.send_message(embed=embed, ephemeral=True)

