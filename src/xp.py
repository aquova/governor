import discord, db, requests, os, shutil, utils
from config import XP_PER_LVL, LVL_CHANS, OWNER, ASSETS_PATH, FONTS_PATH, TMP_PATH
from dataclasses import dataclass, astuple
from math import ceil, floor
from PIL import Image, ImageDraw, ImageFont
from commonbot.user import UserLookup

ul = UserLookup()

@dataclass
class Point:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def shadow_tuple(self):
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
async def get_xp(message):
    author = None
    other_id = ul.parse_mention(message)
    if other_id != None:
        author = discord.utils.get(message.guild.members, id=other_id)

    # If we couldn't find a user, use the message author
    if author == None:
        author = message.author

    xp = db.fetch_user_xp(author.id)
    if author == message.author:
        return f"You have {xp} XP"
    else:
        return f"They have {xp} XP"

"""
Userinfo

Returns a 'rich' post with some of the user's information in it
"""
async def userinfo(message):
    # First, check if the user wants to look up someone else
    author = None
    other_id = ul.parse_mention(message)
    if other_id != None:
        author = discord.utils.get(message.guild.members, id=other_id)

    # If we couldn't find a user, use the message author
    if author == None:
        author = message.author

    username = f"{author.name}#{author.discriminator}"
    # https://strftime.org/ is great if you ever want to change this, FYI
    create_time = author.created_at.strftime("%c")
    join_time = author.joined_at.strftime("%c")
    boost_time = author.premium_since
    is_owner = message.guild.owner == author

    # The first role is always @everyone, so omit it
    roles = [x.name for x in author.roles[1:]]
    role_str = ", ".join(roles)

    embed = discord.Embed(title=username, type="rich", color=author.color)
    if author.nick != None:
        embed.description = f"aka {author.nick}"
    embed.set_thumbnail(url=author.avatar_url)
    embed.add_field(name="ID", value=author.id, inline=False)
    if author.bot:
        embed.add_field(name="Bot?", value="🤖")

    if is_owner:
        embed.add_field(name="Owner?", value="👑")

    embed.add_field(name="created", value=create_time)
    embed.add_field(name="joined", value=join_time)
    if boost_time != None:
        embed.add_field(name="boosted", value=boost_time.strftime("%c"))

    embed.add_field(name="roles", value=role_str, inline=False)

    await message.channel.send(embed=embed)

"""
Render level image

Creates a customized image for the user, showing avatar image, level, name, and rank
"""
async def render_lvl_image(message):
    # Only allow this command if in whitelisted channels
    if not utils.is_valid_channel(message.channel.id, LVL_CHANS):
        return

    # Make image tmp folder if needed
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    # First, check if the user wants to look up someone else
    author = None
    other_id = ul.parse_mention(message)
    if other_id != None:
        author = discord.utils.get(message.guild.members, id=other_id)

    # If we couldn't find a user, use the message author
    if author == None:
        author = message.author

    userid = author.id
    username = author.name
    xp = db.fetch_user_xp(userid)
    lvl = floor(xp / XP_PER_LVL)
    # Calculate what percentage we are to the next level, as a range from 0-10
    bar_num = ceil(10 * (xp - (lvl * XP_PER_LVL)) / XP_PER_LVL)
    rank = db.get_rank(userid)

    out_filename = os.path.join(TMP_PATH, f"{userid}.png")
    avatar_filename = out_filename

    if author.avatar == None:
        avatar_filename = os.path.join(ASSETS_PATH, "default_avatar.png")
    else:
        avatar_url = f"https://cdn.discordapp.com/avatars/{userid}/{author.avatar}.png"

        # Download the user's avatar image to private/tmp
        try:
            response = requests.get(avatar_url, stream=True)
            with open(avatar_filename, 'wb') as outfile:
                shutil.copyfileobj(response.raw, outfile)
            del response
        except requests.exceptions.ConnectionError as e:
            print(f"Issue downloading avatar {avatar_url}. Aborting")
            print(str(e))
            return f"Error accessing avatar URL has occurred. Pinging <@{OWNER}>"

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
    font_12 = ImageFont.truetype(FONT, 12)
    font_14 = ImageFont.truetype(FONT, 14)
    font_22 = ImageFont.truetype(FONT, 22)

    # Draw shadow one pixel down and left
    draw.text(USERNAME_POS.shadow_tuple(), username, BACK_COLOR, font=font_22)
    draw.text(astuple(USERNAME_POS), username, FONT_COLOR, font=font_22)
    # The discriminator needs to be appended on the end of the username, but in a different font size
    username_width = font_22.getsize(username)[0]
    y_offset = font_22.getsize(username)[1] / 6
    draw.text((USERNAME_POS.x + username_width, USERNAME_POS.y + y_offset), f"#{author.discriminator}", BACK_COLOR, font=font_14)

    draw.text(LEVEL_POS.shadow_tuple(), f"Level {lvl}", BACK_COLOR, font=font_22)
    draw.text(astuple(LEVEL_POS), f"Level {lvl}", FONT_COLOR, font=font_22)

    # Since the ranks can be (currentnly) up to 5 digits, adjust dynamically
    rank_text = f"Server Rank : {rank}"
    rank_width = font_14.getsize(rank_text)[0]
    draw.text((RANK_POS.x - rank_width, RANK_POS.y), rank_text, BACK_COLOR, font=font_14)

    # Save and close images
    bg.save(out_filename)
    bg.close()
    avatar.close()
    frame.close()
    small_bar.close()
    large_bar.close()

    # Send image to channel
    with open(out_filename, 'rb') as af:
        df = discord.File(af)
        await message.channel.send(file=df)

    return None
