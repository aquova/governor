from math import floor

from bs4 import BeautifulSoup, Tag
import discord
import requests

import commands
import db
import xp
from client import client
from commonbot.timestamp import calculate_timestamps
from config import MODDER_ROLE, MODDER_URL, XP_PER_LVL

@client.tree.command(name="leaderboard", description="Get the URL for the online leaderboard")
async def lb_context(interaction: discord.Interaction):
    url = await commands.show_lb(None)
    await interaction.response.send_message(url, ephemeral=True)

@client.tree.command(name="ranks", description="List the earnable ranks for the server")
async def ranks_context(interaction: discord.Interaction):
    ranks = await commands.list_ranks(None)
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

@client.tree.context_menu(name="User Info")
async def userinfo_context(interaction: discord.Interaction, user: discord.Member):
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

