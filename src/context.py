import discord
from client import client
import commands
import xp

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
