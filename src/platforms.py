from math import floor

import discord

from config import MOBILE_PLATFORM, NS_PLATFORM, PC_PLATFORM, PS_PLATFORM, VITA_PLATFORM, XBOX_PLATFORM

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
