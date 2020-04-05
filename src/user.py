import discord, re
from utils import remove_command

# Attempts to return a user ID
def parse_mention(message):
    # Users can be mentioned one of three ways:
    # - By pinging them
    # - By their username
    # - By their ID

    user_id = None
    user_id = check_mention(message)

    if user_id == None:
        user_id = check_username(message)

    if user_id == None:
        user_id = check_id(message)

    return user_id

def check_mention(message):
    try:
        return message.mentions[0].id
    except IndexError:
        return None

def check_username(message):
    # Usernames can have spaces, so need to throw away the first word (the command),
    # and then everything after the discriminator
    testUsername = remove_command(message.content)

    try:
        # Some people *coughs* like to put a '@' at beginning of the username.
        # Remove the '@' if it exists at the front of the message
        if testUsername[0] == "@":
            testUsername = testUsername[1:]

        # Parse out the actual username
        user = testUsername.split("#")
        discriminator = user[1].split()[0]
        userFound = discord.utils.get(message.guild.members, name=user[0], discriminator=discriminator)
        if userFound != None:
            return userFound.id
    except IndexError:
        return None

def check_id(message):
    checkID = remove_command(message.content)

    try:
        # If ping is typed out by user using their ID, it doesn't count as a mention
        # Thus, try and match with regex
        checkPing = re.search(r"<@!?(\d+)>", checkID)
        if checkPing != None:
            return checkPing.group(1)

        # Simply verify by attempting to cast to an int. If it doesn't raise an error, return it
        # Lengths of Discord IDs seem to be no longer a constant length, so difficult to verify that way
        int(checkID)
        return checkID
    except (IndexError, ValueError):
        return None
