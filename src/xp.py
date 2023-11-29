import os
import shutil
from math import ceil, floor
from typing import Optional

from bs4 import BeautifulSoup, Tag
import discord
import requests
from PIL import Image, ImageDraw, ImageFont

import db
from commonbot.user import UserLookup
from config import ASSETS_PATH, FONTS_PATH, MODDER_ROLE, MODDER_URL, TMP_PATH, XP_PER_LVL
from utils import to_thread

ul = UserLookup()

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    def shadow_tuple(self) -> tuple[int, int]:
        return (self.x - 1, self.y + 1)

IMG_BG = os.path.join(ASSETS_PATH, "bg_rank.png")
IMG_FRAME = os.path.join(ASSETS_PATH, "bg_rank_border_square.png")
IMG_SM_BAR = os.path.join(ASSETS_PATH, "bg_rank_bar_small.png")
IMG_LG_BAR = os.path.join(ASSETS_PATH, "bg_rank_bar_large.png")
FONT = os.path.join(FONTS_PATH, "Roboto/Roboto-Medium.ttf")
FONT_COLOR = (208, 80, 84)
BACK_COLOR = (82, 31, 33)
USERNAME_POS = Point(90, 8)
LEVEL_POS = Point(90, 63)
RANK_POS = Point(385, 68)
BAR_X = [133, 153, 173, 193, 213, 247, 267, 287, 307, 327]
BAR_Y = 37

"""
Get XP

Returns the given user's XP value, as a formatted string
"""
def get_xp(user: discord.Member) -> str:
    xp = db.fetch_user_xp(user.id)
    monthly_xp = db.fetch_user_monthly_xp(user.id)
    return f"{xp} XP all-time, {monthly_xp} XP this month"

"""
Render level image

Creates a customized image for the user, showing avatar image, level, name, and rank
"""
async def render_lvl_image(user: discord.Member | discord.User) -> Optional[str]:
    # Make image tmp folder if needed
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    userid = user.id
    username = user.name
    xp = db.fetch_user_xp(userid)
    lvl = floor(xp / XP_PER_LVL)
    # Calculate what percentage we are to the next level, as a range from 0-10
    bar_num = ceil(10 * (xp - (lvl * XP_PER_LVL)) / XP_PER_LVL)
    rank = db.get_rank(userid)

    out_filename = os.path.join(TMP_PATH, f"{userid}.png")
    avatar_filename = out_filename

    if user.avatar is None:
        avatar_filename = os.path.join(ASSETS_PATH, "default_avatar.png")
    else:
        avatar_url = user.display_avatar.url

        # Download the user's avatar image to private/tmp
        success = await download_avatar(avatar_url, avatar_filename)
        if not success:
            return None

    # Open image, paste the avatar image, then the frame
    bg = Image.open(IMG_BG)
    avatar = Image.open(avatar_filename).convert("RGBA")
    frame = Image.open(IMG_FRAME)
    small_bar = Image.open(IMG_SM_BAR)
    large_bar = Image.open(IMG_LG_BAR)

    avatar = avatar.resize((68, 68))
    bg.paste(avatar, (16, 14), avatar)
    bg.paste(frame, (14, 12), frame)

    for i in range(0, bar_num):
        # The 5th and 10th bars are large bars
        if i % 5 == 4:
            bg.paste(large_bar, (BAR_X[i], BAR_Y), large_bar)
        else:
            bg.paste(small_bar, (BAR_X[i], BAR_Y), small_bar)

    # Add the information text to the image
    draw = ImageDraw.Draw(bg)
    font_14 = ImageFont.truetype(FONT, 14)
    font_22 = ImageFont.truetype(FONT, 22)

    # Draw shadow one pixel down and left
    draw.text(USERNAME_POS.shadow_tuple(), username, BACK_COLOR, font=font_22)
    draw.text(USERNAME_POS.as_tuple(), username, FONT_COLOR, font=font_22)

    draw.text(LEVEL_POS.shadow_tuple(), f"Level {lvl}", BACK_COLOR, font=font_22)
    draw.text(LEVEL_POS.as_tuple(), f"Level {lvl}", FONT_COLOR, font=font_22)

    # Since the ranks can be (currentnly) up to 5 digits, adjust dynamically
    rank_text = f"Server Rank : {rank}"
    rank_width = font_14.getlength(rank_text)
    draw.text((RANK_POS.x - rank_width, RANK_POS.y), rank_text, BACK_COLOR, font=font_14)

    # Save and close images
    bg.save(out_filename)
    bg.close()
    avatar.close()
    frame.close()
    small_bar.close()
    large_bar.close()

    return out_filename

def _find_modder_info(uid: str) -> list[tuple[str, str]]:
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

def create_user_info_embed(user: discord.Member) -> discord.Embed:
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
        mod_info = _find_modder_info(str(user.id))
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
    return embed

@to_thread
def download_avatar(url: str, filename: str) -> bool:
    try:
        response = requests.get(url, stream=True)
        with open(filename, 'wb') as outfile:
            shutil.copyfileobj(response.raw, outfile)
        del response
        return True
    except requests.exceptions.ConnectionError as err:
        print(f"Issue downloading avatar {url}. Aborting")
        print(str(err))
        return False
