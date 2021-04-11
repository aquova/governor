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
    return words[0].lower()

"""
Remove command

Removes the command invocation, to return just the payload, if any

Input: mes - message to modify - str
"""
def remove_command(mes):
    first = mes.split()[0]
    # Want to simply chop off first word rather than split, to preserve whitespace
    start = len(first) + 1
    return mes[start:]

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

"""
Is valid channel

Determines if allowed to post in the current channel
Does what it says on the tin
"""
def is_valid_channel(chan, chan_list):
    return chan in chan_list
