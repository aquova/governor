# Functions related to Discord server events (not API events)

import discord
from config import ADMIN_ACCESS, XP_PER_LVL
from tracker import Tracker

async def award_event_prize(reaction, reactor, tr):
    # TODO: Put these in config.json
    ROLE_IDS = [281902740785856513, 703675309656113252]
    author = reaction.message.author

    # Only give reward if giver is an admin, and correct emoji was used
    # Can't use requires_admin wrapper as there is no message object from the event
    check_roles = [x.id for x in reactor.roles]
    if ADMIN_ACCESS in check_roles:
        emoji_name = reaction.emoji if type(reaction.emoji) == str else reaction.emoji.name
        if emoji_name == "SDVpufferspring":
            # Award three levels
            await tr.give_xp(author, 3 * XP_PER_LVL)
            user_roles = author.roles
            for role in ROLE_IDS:
                new_role = discord.utils.get(author.guild.roles, id=role)
                if new_role != None and new_role not in user_roles:
                    user_roles.append(new_role)

            await author.edit(roles=user_roles)
