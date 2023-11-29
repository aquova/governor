import asyncio
import functools
from typing import Callable, Coroutine

from config import RANKS, SERVER_URL


class CustomCommandFlags:
    NONE =      0b0000     # No limitations
    ADMIN =     0b0001     # Created by an admin
    LIMITED =   0b0010     # Usage can be limited to some channels

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

def to_thread(func: Callable) -> Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
