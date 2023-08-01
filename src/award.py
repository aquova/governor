import discord

import achievements
import client
import config
import db

ROLES = {
    222591661903970304: achievements.AchivementID.VILLAGER,
    744929308388098068: achievements.AchivementID.COWPOKE,
    176445608201158657: achievements.AchivementID.FARMER,
    571537175741464576: achievements.AchivementID.SHEPHERD,
    230788741084610560: achievements.AchivementID.RANCHER,
    405556651245043712: achievements.AchivementID.CROPMASTER,
    405556702923063296: achievements.AchivementID.DESPERADO,
    222588384344801280: achievements.AchivementID.ARTISAN,
    363441846837575690: achievements.AchivementID.PIXELSMITH,
    475536776774025217: achievements.AchivementID.CONTENTSMITH,
    193021029122179072: achievements.AchivementID.BLACKSMITH,
    976288616215105576: achievements.AchivementID.JUKEBOX,
}

@client.client.event
async def on_guild_available(guild: discord.Guild):
    db.initialize()
    db.initialize_achievements(achievements.ACHIEVEMENTS)
    for member in guild.members:
        print(f"Checking user {str(member)}")
        for role in member.roles:
            if role.id in ROLES:
                db.earn_achievement(member.id, ROLES[role.id].value)

client.client.run(config.DISCORD_KEY)
