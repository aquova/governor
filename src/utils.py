import asyncio
import functools
from typing import Callable, Coroutine, Optional

from commonbot.utils import check_roles
from config import ADMIN_ACCESS, DEFINE_ACCESS, RANKS, SERVER_URL


class CustomCommandFlags:
    NONE =      0b0000     # No limitations
    ADMIN =     0b0001     # Created by an admin
    LIMITED =   0b0010     # Usage can be limited to some channels

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

"""
Requires define

Wrapper function for commands that requires admin access or *all* defined roles in config.DEFINE_ACCESS
"""
def requires_define(func: Callable) -> Optional[Callable]:
    async def wrapper(*args, **kwargs):
        message = args[-1]

        user_roles = [x.id for x in message.author.roles]
        allow_access = True
        for role in DEFINE_ACCESS:
            if role not in user_roles:
                allow_access = False
                break

        if not allow_access:
            allow_access = check_roles(message.author, ADMIN_ACCESS)

        if allow_access:
            return await func(*args, **kwargs)
        else:
            return None

    return wrapper

"""
Requires admin

Wrapper function for commands that has them do nothing if the author doesn't have the admin role
"""
def requires_admin(func: Callable) -> Optional[Callable]:
    async def wrapper(*args, **kwargs):
        # expect message to be the last argument
        message = args[-1]

        if check_roles(message.author, ADMIN_ACCESS):
            return await func(*args, **kwargs)
        else:
            return None

    return wrapper

def to_thread(func: Callable) -> Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
