# Functions related to Discord server events (not API events)

import discord, db, requests, os, shutil
from config import ADMIN_ACCESS, PUZZLE_EVENTS, XP_PER_LVL, CURRENT_EVENTS
from tracker import Tracker

async def award_event_prize(reaction, reactor, tr):
    author = reaction.message.author

    # Only give reward if giver is an admin, and correct emoji was used
    # Can't use requires_admin wrapper as there is no message object from the event
    check_roles = [x.id for x in reactor.roles]
    if ADMIN_ACCESS in check_roles:
        emoji_name = reaction.emoji if type(reaction.emoji) == str else reaction.emoji.name
        for event in CURRENT_EVENTS:
            if emoji_name == event['emoji_name']:
                # Award three levels
                await tr.give_xp(author, 3 * XP_PER_LVL)
                user_roles = author.roles
                for role in event['ids']:
                    new_role = discord.utils.get(author.guild.roles, id=role)
                    if new_role != None and new_role not in user_roles:
                        user_roles.append(new_role)

                await author.edit(roles=user_roles)
                db.add_raffle(author.id)
                # Add our own emoji, so we can show that it went through
                emoji = discord.utils.get(author.guild.emojis, name=emoji_name)
                await reaction.message.add_reaction(emoji)

async def event_check(message):
    await _check_hidden_task(message)

async def _check_hidden_task(message):
    # For events where other members shouldn't see entries we need to:
    # - Download and save the entry image
    # - Enter that and their info into a table
    # - Delete their post in chat
    # - Ping them with a thumbs up, showing their entry was received
    # - Auto delete everything that doesn't have an image

    # If this isn't a valid event channel, leave
    if message.channel.id not in PUZZLE_EVENTS:
        return

    # Make the events folder if it doesn't exist
    folder = f"../private/events/{message.channel.name}"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Check if the event's master entry log exists
    entrants = f"{folder}/members.md"
    if not os.path.exists(entrants):
        with open(entrants, 'w') as eventfile:
            eventfile.write(f"# {message.channel.name}\n\n| User | ID | Submission |\n| -- | -- | -- |\n")

    author = message.author
    valid = False
    for a in message.attachments:
        # This limits submissions to video/image
        # TODO: Find a way to only allow images
        if a.height == None:
            continue

        valid = True
        filename = f"{author.id}_{a.filename}"
        response = requests.get(a.url, stream=True)
        with open(f"{folder}/{filename}", 'wb') as outfile:
            shutil.copyfileobj(response.raw, outfile)
        del response

        event_entry = f"| {author.name}#{author.discriminator} | {author.id} | ![]({filename}) |\n"
        with open(entrants, 'a') as eventfile:
            eventfile.write(event_entry)

    if valid:
        db.add_raffle(author.id)
        await message.channel.send(f"<@{author.id}> :thumbsup:")

    # Valid entry or not, we want to delete it
    await message.delete()
