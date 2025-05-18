# pyright: reportAny=false, reportExplicitAny=false

import asyncio
import functools
from textwrap import wrap
from typing import Any, Callable, final, TypeVar

import discord

from config import LIMIT_CHANS, NO_SLOWMODE, RANKS, SERVER_URL, XP_OFF

CHAR_LIMIT = 1990 # The actual limit is 2000, but we'll have a buffer


@final
class CustomCommandFlags:
    NONE =      0b0000     # No limitations
    ADMIN =     0b0001     # Created by an admin
    LIMITED =   0b0010     # Usage can be limited to some channels

def check_roles(user: discord.Member | discord.User, valid_roles: list[int]) -> bool:
    """
    Check Roles

    Checks if the user has any of the roles in the list (by ID)
    """
    if isinstance(user, discord.User):
        return False
    for role in valid_roles:
        if user.get_role(role):
            return True
    return False

def show_lb() -> str:
    """
    Show leaderboard

    Posts the URL for the online leaderboard
    """
    return f"{SERVER_URL}/leaderboard.php"

def list_ranks() -> str:
    """
    List ranks

    Lists the available earnable rank roles, and their levels
    """
    output = ""
    for rank in RANKS:
        output += f"Level {rank.level}: {rank.name}\n"
    return output

def get_bot_info() -> str:
    """
    Get Bot Info

    Get info about bot settings
    """
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
    """
    Split message

    Splits a string into a list so none of the substrings breaks Discord's character limit
    """
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
    """
    Send Message

    Helper function to send a string into a Discord chat. Will break up the message into pieces as to not break the character limit, if needed.

    Returns the Discord Message object for the first posted
    """
    messages = split_message(message)
    first_id = None
    for msg in messages:
        if len(msg) > 0:
            mid = await channel.send(msg)
            first_id = mid if first_id is None else first_id
    return first_id

# I don't understand this type annotation either, but the internet said it was right and it shut the linter up
R = TypeVar('R')
def to_thread(func: Callable[..., R]) -> Callable[..., Any]:
    """
    To thread

    Utility function to convert a callable function to run in a coroutine
    """
    @functools.wraps(func)
    async def wrapper(*args: ..., **kwargs: Any) -> R:
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

def flatten_index(index: list[Any]) -> list[Any]:
    """
    Flatten Nexus Files Index

    Flattens the Nexusmods file index to be a single array of files with no directories or sub-arrays.
    """
    result: list[Any] = []

    def _flatten(node: Any):
        if 'children' in node:
            for child in node['children']:
                _flatten(child)
        elif 'type' in node and node['type'] == 'file':
            result.append(node)

    if 'children' in index:
        for child in index['children']:
            _flatten(child)

    return result
