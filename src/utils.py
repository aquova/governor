from config import ADMIN_ACCESS

"""
Requires admin

Wrapper function for commands that has them do nothing if the author doesn't have the admin role
"""
def requires_admin(func):
    async def wrapper(*args, **kwargs):
        # expect message to be the last argument
        message = args[-1]

        roles = [x.id for x in message.author.roles]
        if ADMIN_ACCESS not in roles:
            return None

        return await func(*args, **kwargs)
    return wrapper
