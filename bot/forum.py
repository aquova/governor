import asyncio

import discord

from config import RESOLVED_TAG, PROGRESS_TAGS, OPEN_TAG, FORUM_CHAN

async def apply_open_tag(thread: discord.Thread):
    """
    Apply open tag

    Applies the "Open" tag to new posts in the help forum channel

    The open tag ID is defined as the OPEN_TAG config item, and the help forum channel ID is defined as FORUM_CHAN

    This function also posts a helpful introductory message to the thread as well
    """
    if not thread.parent_id == FORUM_CHAN:
        return
    open_tag = thread.parent.get_tag(OPEN_TAG)
    if open_tag not in thread.applied_tags and open_tag is not None:
        tags = thread.applied_tags
        tags.append(open_tag)
        await thread.edit(applied_tags=tags)

    # We aren't allowed to be the first post in a thread. Sleep briefly so the user's post has a chance to go through
    await asyncio.sleep(2)
    await thread.send("Hi! While you’re waiting for support, please ensure you have uploaded your SMAPI log. Instructions can be found [here](https://smapi.io/log).\nThreads posted are subject to the posting guidelines.\nIf your issue is resolved or you no longer need help, please do NOT delete or close your post. Instead, just add the Mark As Resolved tag or leave a message stating you no longer need help.")

async def resolve_thread(channel: discord.Thread):
    """
    Resolve thread

    Marks a thread in the help forum channel as resolved. This is done by locking and archiving the thread, removing all tags that are considered "in progress", and adding a resolved tag.

    The resolved tag ID is defined as the RESOLVED_TAG config item, a list of in progress tag IDs are defined in PROGRESS_TAGS, and the help forum channel ID is defined as FORUM_CHAN
    """
    resolve_tag = channel.parent.get_tag(RESOLVED_TAG)
    tags = []
    if resolve_tag is not None:
        tags.append(resolve_tag)
    for tag in channel.applied_tags:
        if tag is not None and tag.id not in PROGRESS_TAGS:
            tags.append(tag)
    await channel.edit(locked=True, archived=True, applied_tags=tags)
