from datetime import datetime, timezone
from typing import override

import discord
from discord.ext import commands, tasks

import db
from config import YAPPER_ROLE

COOLDOWN = 4    # Number of weeks until a user can win again
WINNERS = 5     # Number of winners per week

class Yapper(commands.Cog):
    def __init__(self):
        self.server: discord.Guild | None = None

    def setup(self, guild: discord.Guild):
        self.server = guild
        self._award_winners.start()

    @override
    async def cog_unload(self):
        self._award_winners.cancel()

    @tasks.loop(hours=24)
    async def _award_winners(self):
        if self.server is None:
            return

        curr = datetime.now(timezone.utc)
        week = db.get_week(curr) - 1
        cutoff = week - COOLDOWN
        # Check if we've already handled this week
        if len(db.get_old_yappers(week)) > 0:
            return

        yapper = self.server.get_role(YAPPER_ROLE)
        if yapper is None:
            return
        # Begin by removing last week's winners' roles
        last = db.get_old_yappers(week - 1)
        for old in last:
            user = self.server.get_member(old)
            if user is not None:
                await user.remove_roles(yapper)

        leaders = db.get_weekly_leaders()
        cnt = 0
        for leader in leaders:
            if cnt == WINNERS:
                break
            last = db.get_last_yapper_victory(leader.uid)
            if last is None or last < cutoff:
                user = self.server.get_member(leader.uid)
                if user is not None:
                    await user.add_roles(yapper)
                    db.add_yapper(leader.uid, week)
                    cnt += 1

