from config import ADMIN_ACCESS, DEFINE_ACCESS
from commonbot.utils import check_roles
from typing import Callable, Optional

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
