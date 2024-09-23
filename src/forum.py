import discord

from config import RESOLVED_TAG, PROGRESS_TAGS, OPEN_TAG, FORUM_CHAN

async def apply_open_tag(thread: discord.Thread):
    if not thread.parent_id == FORUM_CHAN:
        return
    open_tag = thread.parent.get_tag(OPEN_TAG)
    if open_tag not in thread.applied_tags and open_tag is not None:
        tags = thread.applied_tags
        tags.append(open_tag)
        await thread.edit(applied_tags=tags)

async def resolve_thread(channel: discord.Thread):
    resolve_tag = channel.parent.get_tag(RESOLVED_TAG)
    tags = []
    if resolve_tag is not None:
        tags.append(resolve_tag)
    for tag in channel.applied_tags:
        if tag is not None and tag.id not in PROGRESS_TAGS:
            tags.append(tag)
    await channel.edit(locked=True, archived=True, applied_tags=tags)
