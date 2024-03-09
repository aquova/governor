import asyncio
import functools
from textwrap import wrap
from typing import Callable, Coroutine

import discord

from config import LIMIT_CHANS, NO_SLOWMODE, RANKS, SERVER_URL, XP_OFF

CHAR_LIMIT = 1990 # The actual limit is 2000, but we'll have a buffer


class CustomCommandFlags:
    NONE =      0b0000     # No limitations
    ADMIN =     0b0001     # Created by an admin
    LIMITED =   0b0010     # Usage can be limited to some channels

"""
Check Roles

Checks if the user has any of the roles in the list (by ID)
"""
def check_roles(user: discord.Member | discord.User, valid_roles: list[int]) -> bool:
    if isinstance(user, discord.User):
        return False
    for role in valid_roles:
        if user.get_role(role):
            return True
    return False

"""
Show leaderboard

Posts the URL for the online leaderboard
"""
def show_lb() -> str:
    return f"{SERVER_URL}/leaderboard.php"

"""
List ranks

Lists the available earnable rank roles, and their levels
"""
def list_ranks() -> str:
    output = ""
    for rank in RANKS:
        output += f"Level {rank['level']}: {rank['name']}\n"
    return output

"""
Get Bot Info

Get info about bot settings
"""
def get_bot_info() -> str:
    slow_c = ", ".join([f"<#{x}>" for x in NO_SLOWMODE])
    xp_c = ", ".join([f"<#{x}>" for x in XP_OFF])
    limit_c = ", ".join([f"<#{x}>" for x in LIMIT_CHANS])
    response = (
        f"Dynamic slowmode is disabled in {slow_c}\n"
        f"Users do not gain XP in {xp_c}\n"
        f"Commands can be disabled in {limit_c}\n"
    )
    return response

def split_message(message: str) -> list[str]:
    messages = message.split('\n')
    to_send = [messages[0]]
    for msg in messages[1:]:
        if len(msg) >= CHAR_LIMIT:
            to_send += wrap(msg, width=CHAR_LIMIT)
        elif len(msg) + len(to_send[-1]) < CHAR_LIMIT:
            to_send[-1] += f"\n{msg}"
        else:
            to_send.append(msg)
    return to_send

async def send_message(message: str, channel: discord.TextChannel | discord.Thread) -> discord.Message | None:
    messages = split_message(message)
    first_id = None
    for msg in messages:
        if len(msg) > 0:
            mid = await channel.send(msg)
            first_id = mid if first_id is None else first_id
    return first_id

def to_thread(func: Callable) -> Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

"""
Flatten Nexus Files Index

Flattens the Nexusmods file index to be a single array of files with no directories or sub-arrays.
"""
def flatten_index(index: list) -> list:
    result = []

    def _flatten(node):
        if 'children' in node:
            for child in node['children']:
                _flatten(child)
        elif 'type' in node and node['type'] == 'file':
            result.append(node)

    for child in index['children']:
        _flatten(child)

    return result
