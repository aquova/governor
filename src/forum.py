import discord

from config import RESOLVED_TAG, OPEN_TAGS

async def resolve_thread(channel: discord.Thread):
    resolve_tag = channel.parent.get_tag(RESOLVED_TAG)
    tags = []
    if resolve_tag is not None:
        tags.append(resolve_tag)
    for tag in channel.applied_tags:
        if tag is not None and tag.id not in OPEN_TAGS:
            tags.append(tag)
    await channel.edit(locked=True, archived=True, applied_tags=tags)
