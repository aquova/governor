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
