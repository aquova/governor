import db
from datetime import datetime, timedelta, timezone
import asyncio, random
from config import GAME_ANNOUNCE_TIME
from utils import requires_admin

import commonbot.utils

ANNOUNCE_MESSAGES = [
    "Oh ho ho, what are all these free games I've found?",
    "Wow, I still remember how delicious the Luau soup was. Here are some free games:",
    "Here are today's free games!"
]

"""
Game Timer

Manages sending out game announcements at a regular interval.
Can only handle one announcement channel for one server.
"""
class GameTimer:
    def __init__(self):
        self.task = None

    def start(self, channel):
        if not self.task:
            self._channel = channel
            self.task = asyncio.create_task(self._announce_games())

    async def _announce_games(self):
        while True:
            await self._wait_until_next_announcement()

            games = db.get_games()

            if len(games) != 0:
                # generate message
                formatted_games = "\n".join(games)
                announcement = random.choice(ANNOUNCE_MESSAGES)
                message = f"{announcement}\n\n{formatted_games}"

                # send message
                await self._channel.send(message)

                # clear games
                db.clear_games()

    @staticmethod
    async def _wait_until_next_announcement():
        next_announcement = get_delta_to_next_announcement()

        await asyncio.sleep(next_announcement.total_seconds())


"""
Add game

Adds a game to be announced
"""
@requires_admin
async def add_game(message):
    game = commonbot.utils.strip_words(message.content, 1).strip()
    if len(game) == 0:
        return "Can't add game: no message provided."

    games = db.get_games()
    time_info = get_next_announcement_info()

    if game in games:
       return f"That game (and {len(games) - 1} other(s)) is already going to be announced at {time_info}."

    db.add_game(game)

    return f"Game added! {len(games) + 1} game(s) will be announced at {time_info}."

"""
Get games

Returns the list of games to be announced
"""
@requires_admin
async def get_games(message):
    games = db.get_games()

    time_info = get_next_announcement_info()

    if len(games) != 0:
        formatted_games = "\n".join(games)

        return f"The following games will be announced at {time_info}:\n{formatted_games}"
    else:
        return f"There are no games to announce so the next announcement at {time_info} will be skipped."

"""
Clear games

Clears all games that are being announced
"""
@requires_admin
async def clear_games(message):
    db.clear_games()

    return "Games cleared!"


"""
Get next announcement info

Returns a string representing the time when the next game announcement will happen. Inlcudes the UTC time and duration until that time.
"""
def get_next_announcement_info():
    time_utc = GAME_ANNOUNCE_TIME.strftime("%H:%M UTC")
    remaining = get_delta_to_next_announcement()

    hours, remainder = divmod(remaining.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)

    return f"{time_utc} ({int(hours)}h{int(minutes)}m left)"

"""
Get delta to next announcement

Gets a timedelta to the next announcement time.

If the current time today is before the configured time, the timedelta will be to the announcement time today. Otherwise it will be for the announcement time tomorrow.
"""
def get_delta_to_next_announcement():
    now = datetime.now(timezone.utc)
    announcement = now.replace(hour=GAME_ANNOUNCE_TIME.hour, minute=GAME_ANNOUNCE_TIME.minute)

    if announcement <= now:
        announcement += timedelta(days=1)

    return announcement - now
