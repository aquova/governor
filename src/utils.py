from config import ADMIN_ACCESS

"""
Strip prefix

Removes the command prefix from a message

Input: mes - message to modify - str
"""
def strip_prefix(mes):
    # TODO: Make this more prefix-agnostic
    return mes[1:]

"""
Get command

Returns the first word of a string

Input: mes - message to modify - str
"""
def get_command(mes):
    words = mes.split()
    return words[0]

"""
Remove command

Removes the command invocation, to return just the payload, if any

Input: mes - message to modify - str
"""
def remove_command(mes):
    request = mes.split()[1:]
    return " ".join(request)

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
