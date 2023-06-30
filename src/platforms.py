from math import floor
from typing import cast

import discord

from commonbot.utils import strip_words, get_first_word

from config import CMD_PREFIX, PC_PLATFORM, XBOX_PLATFORM, PS_PLATFORM, NS_PLATFORM, MOBILE_PLATFORM, VITA_PLATFORM
from utils import requires_admin

PLATFORMS = {
    "Xbox": XBOX_PLATFORM,
    "PlayStation": PS_PLATFORM,
    "Switch": NS_PLATFORM,
    "PC/Mac/Linux": PC_PLATFORM,
    "Mobile": MOBILE_PLATFORM,
    "PS Vita": VITA_PLATFORM
}

class PlatformWidgetButton(discord.ui.Button):
    def __init__(self, txt: str, row: int):
        custom_id = f"platform_ui:{txt}"
        super().__init__(style=discord.ButtonStyle.primary, label=txt, row=row, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        if isinstance(interaction.user, discord.User) or self.label is None:
            return

        role_id = PLATFORMS[self.label]
        role = discord.utils.get(interaction.user.guild.roles, id=role_id)
        if role is None:
            return
        if interaction.user.get_role(role_id):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{self.label} role removed!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{self.label} role added!", ephemeral=True)

class PlatformWidget(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        idx = 0
        for platform, _ in PLATFORMS.items():
            self.add_item(PlatformWidgetButton(platform, floor(idx / 3)))
            idx += 1

@requires_admin
async def post_widget(message: discord.Message) -> str:
    try:
        payload = strip_words(message.content, 1)
        chan_id = get_first_word(payload)
        if message.guild is None:
            return ""
        channel = cast(discord.TextChannel, discord.utils.get(message.guild.channels, id=int(chan_id)))
        if channel is None:
            raise ValueError
        await channel.send("Assign yourself any of the platforms you use!", view=PlatformWidget())
        return ""
    except ValueError:
        return f"I was unable to find a channel ID in that message. `{CMD_PREFIX}roles CHAN_ID`"
