import discord

class SayModal(discord.ui.Modal):
    def __init__(self, channel: discord.TextChannel | discord.Thread):
        super().__init__(title="Say a message as the bot")
        self.channel = channel
        self.content = discord.ui.TextInput(
            label="Bot message",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.content)

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.content.value)
        await interaction.response.send_message("Message sent!")

class EditModal(discord.ui.Modal):
    def __init__(self, channel: discord.TextChannel | discord.Thread, message_id: str):
        super().__init__(title="Edit a bot message")
        self.channel = channel
        self.message_id = message_id
        self.content = discord.ui.TextInput(
            label="New bot message",
            style=discord.TextStyle.long,
            required=True
        )
        self.add_item(self.content)

    async def on_submit(self, interaction: discord.Interaction):
        from client import client

        # Although discord.py wants IDs to be ints, Discord's UI considers their own IDs too long to be an int
        # So we have to ask users for a string, then convert here to int
        try:
            message_int = int(self.message_id)
        except ValueError:
            await interaction.response.send_message("That's not a valid ID", ephemeral=True)
            return

        edit_message = await self.channel.fetch_message(message_int)
        if edit_message is None:
            await interaction.response.send_message("I was unable to find a message with that ID", ephemeral=True)
            return

        if edit_message.author != client.user:
            await interaction.response.send_message("I didn't write that message! I can't edit that!", ephemeral=True)
            return

        await edit_message.edit(content=self.content.value)
        await interaction.response.send_message("Message edited!")

