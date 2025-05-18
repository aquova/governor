from typing import override

import discord

class SayModal(discord.ui.Modal):
    """
    Say Modal

    Subclass of discord.ui.Modal to provide a modal for users to speak 'as the bot'
    """
    def __init__(self, channel: discord.TextChannel | discord.Thread):
        super().__init__(title="Say a message as the bot")
        self.channel: discord.TextChannel | discord.Thread = channel
        self.content: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
            label="Bot message",
            style=discord.TextStyle.long,
            max_length=1999,
            required=True
        )
        self.add_item(self.content)

    @override
    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.content.value)
        await interaction.response.send_message("Message sent!")

class EditModal(discord.ui.Modal):
    """
    Edit Modal

    Subclass of discord.ui.Modal to provide users a way to edit a message posted 'as the bot'
    """
    def __init__(self, client: discord.Client, channel: discord.TextChannel | discord.Thread, message_id: str):
        super().__init__(title="Edit a bot message")
        self.client: discord.Client = client
        self.channel: discord.TextChannel | discord.Thread = channel
        self.message_id: str = message_id
        self.content: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
            label="New bot message",
            style=discord.TextStyle.long,
            max_length=1999,
            required=True
        )
        self.add_item(self.content)

    @override
    async def on_submit(self, interaction: discord.Interaction):
        # Although discord.py wants IDs to be ints, Discord's UI considers their own IDs too long to be an int
        # So we have to ask users for a string, then convert here to int
        try:
            message_int = int(self.message_id)
        except ValueError:
            await interaction.response.send_message("That's not a valid ID", ephemeral=True)
            return

        try:
            edit_message = await self.channel.fetch_message(message_int)
        except discord.NotFound:
            await interaction.response.send_message("I was unable to find a message with that ID", ephemeral=True)
            return

        if edit_message.author != self.client.user:
            await interaction.response.send_message("I didn't write that message! I can't edit that!", ephemeral=True)
            return

        await edit_message.edit(content=self.content.value)
        await interaction.response.send_message("Message edited!")

