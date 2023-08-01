import discord
from enum import Enum

from config import CMD_PREFIX
import db
from utils import requires_admin

from commonbot.user import UserLookup

class AchivementID(Enum):
    VILLAGER        = 0
    COWPOKE         = 1
    FARMER          = 2
    SHEPHERD        = 3
    RANCHER         = 4
    CROPMASTER      = 5
    DESPERADO       = 6
    BLACKSMITH      = 7
    CONTENTSMITH    = 8
    PIXELSMITH      = 9
    ARTISAN         = 10
    JUKEBOX         = 11
    MONTHLY         = 12
    EVENT           = 13
    STAFF           = 14

    NUM_ACHIVEMENTS = 15 # Update this when new achievements added

# Order needs to align with AchievementID
ACHIEVEMENTS = [
    ("Villager",                "For reaching level 1", ""),
    ("Cowpoke",                 "For reaching level 5", ""),
    ("Farmer",                  "For reaching level 25", ""),
    ("Shepherd",                "For reaching level 100", ""),
    ("Rancher",                 "For reaching level 250", ""),
    ("Cropmaster",              "For reaching level 500", ""),
    ("Desperado",               "For reaching level 1000", ""),
    ("Blacksmith",              "For writing a SMAPI mod", ""),
    ("Contentsmith",            "For writing a content mod", ""),
    ("Pixelsmith",              "For making an asset mod", ""),
    ("Artisan",                 "For contributing great artwork", ""),
    ("Jukebox Junkie",          "For being a fan of the jukebox", ""),
    ("Monthly Mayhem",          "For finishing the month on the leaderboard", ""),
    ("Festival Attendee",       "For participating in an event", ""),
    ("Staff Awarded",           "For being a good citizen in the eyes of the Junimo", ""),
]

assert(len(ACHIEVEMENTS) == AchivementID.NUM_ACHIVEMENTS.value)

@requires_admin
async def give_achievement(message: discord.Message) -> str:
    try:
        guild = message.guild
        if guild is None:
            return ""

        ul = UserLookup()
        userid = ul.parse_id(message)
        # Treat last word as achievement ID to unlock
        aid = int(message.content.split(" ")[-1])

        if AchivementID.NUM_ACHIVEMENTS.value <= aid:
            return "That is not a valid achievement value."
        if userid is not None:
            db.earn_achievement(userid, aid)
            return f"Achivement {ACHIEVEMENTS[aid].name} awarded to <@{userid}>"
        return f"Was unable to understand that message: `{CMD_PREFIX}unlock USER ACHIEVEMENT_ID`"
    except (IndexError, ValueError):
        return f"`{CMD_PREFIX}unlock USER ACHIEVEMENT_ID`"

async def show_achievements(message: discord.Message) -> str:
    author = message.author.id
    ul = UserLookup()
    other_uid = ul.parse_id(message)
    if other_uid is not None:
        author = other_uid

    a_list = db.get_achievements(author)
    return '\n'.join([f"{ACHIEVEMENTS[x][0]} - {ACHIEVEMENTS[x][1]}" for x in a_list])

async def list_achievements(_: discord.Message) -> str:
    a_list = '\n'.join([f"{index}: {item[0]} - {item[1]}" for index, item in enumerate(ACHIEVEMENTS)])
    return a_list

