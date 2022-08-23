import asyncio
from datetime import datetime, timedelta, timezone
import random

import discord

import commonbot.utils
import requests

import db
from config import GAME_ANNOUNCE_TIME
from utils import requires_admin

ANNOUNCE_MESSAGES = [
    "Oh ho ho, what are all these free games I've found?",
    "Wow, I still remember how delicious the Luau soup was. Here are some free games:",
    "Here are today's free games!",
    "Hmm, I found these free games next to some purple shorts:",
    "Back in my day, free games cost two nickels:",
    "Rock lobster bisque is my favorite soup to eat while playing free games:"
]


class GameTimer:
    """
    Game Timer

    Manages sending out game announcements at a regular interval.
    Can only handle one announcement channel for one server.

    Optionally automatically retrieves epic games that became free the current day before announcing games.

    Currently, the announcement runs once a day.

    If the announcement is made to run multiple times in one day, any posted epic games will be posted every time.
    This is because, as is, retrieved epic games for an announcement are not remembered after that announcement.

    If the announcement frequency is ever increased to be more than 1 per day,
    the auto retrieved games already posted will need to be remembered somehow.
    """
    def __init__(self):
        self._channel = None
        self.task = None
        self.should_add_epic_games = None

    def start(self, channel: discord.TextChannel, add_epic_games: bool):
        if self._channel is not None:
            raise Exception("GameTimer already started")

        self._channel = channel
        self.task = asyncio.create_task(self._announce_games())
        self.should_add_epic_games = add_epic_games

    @requires_admin
    async def post_games(self, _) -> str:
        await self._send_message()
        return "Games posted"

    async def _announce_games(self):
        while True:
            await self._wait_until_next_announcement()

            if self.should_add_epic_games:
                self._add_epic_games()

            await self._send_message()

    async def _send_message(self):
        games = db.get_games()

        if len(games) != 0:
            formatted_games = "\n".join(games)
            announcement = random.choice(ANNOUNCE_MESSAGES)
            message = f"{announcement}\n\n{formatted_games}"

            await self._channel.send(message)
            db.clear_games()

    @staticmethod
    async def _wait_until_next_announcement():
        next_announcement = get_delta_to_next_announcement()

        await asyncio.sleep(next_announcement.total_seconds())

    def _add_epic_games(self):
        games_to_add = self._get_epic_games()
        existing_games = db.get_games()

        for game_to_add in games_to_add:
            name, url = game_to_add["name"], game_to_add["url"]
            if not contains_substring(url, existing_games):
                # eg_print(f"{name}: added to next announcement")
                db.add_game(f"{name}: <https://store.epicgames.com/en-US/p/{url}>")

    @staticmethod
    def _get_epic_games() -> list[dict[str, str]]:
        """
        This retrieves epic games newly available for free today. US region only.
        The parsing is *very* hacky, but to be fair, so is the data format.
        :return: A list of newly free games.
        """
        try:
            resp = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?country=US")
        except Exception as e:
            eg_print(f"Couldn't get data: {e}")
            return []

        if resp.status_code != 200:
            eg_print(f"Couldn't get data: {resp.status_code}: {resp.text}")
            return []

        try:
            games = resp.json()["data"]["Catalog"]["searchStore"]["elements"]
        except Exception as e:
            eg_print(f"Couldn't parse data: {e}")
            return []

        # eg_print(f"EG API returned {len(games)} games")
        games_to_add = []
        for game in games:
            try:
                name = game["title"]
                url = game["productSlug"]
                if url is None and len(game["catalogNs"]["mappings"]) > 0:
                    url = game["catalogNs"]["mappings"][0]["pageSlug"]

                if url is None:
                    eg_print(f"{name}: Could not get URL, skipping")
                    continue

                if game["price"]["totalPrice"]["discountPrice"] != 0:
                    # eg_print(f"{name}: not free, skipping")
                    continue

                # When there is no promotion the promotions field is a mess:
                # sometimes null, sometimes an empty object, sometimes a list of no objects
                # Wrap in try/catch and assume failing to parse it means it's not on sale rather than a parse error
                try:
                    start_date = datetime.strptime(
                        game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["startDate"],
                        "%Y-%m-%dT%H:%M:%S.%fZ")
                except Exception:
                    # eg_print(f"{name}: not on sale this week, skipping")
                    continue
            except Exception as e:
                eg_print(f"Couldn't parse game: {e}")
                continue

            # Check the current day against the day the game became free. If the game became free today, add it
            if datetime.utcnow().date() != start_date.date():
                # eg_print(f"{name}: not available today, is/was available on {start_date.date()}, skipping")
                continue

            games_to_add.append({"name": name, "url": url})

        return games_to_add


def eg_print(msg: str):
    """
    eg_print is equivalent to print except it adds an epic games prefix to make reading logs easier.
    """
    print(f"epic_games_auto_add: {msg}")


@requires_admin
async def add_game(message: discord.Message) -> str:
    """
    Add game

    Adds a game to be announced
    """
    game = commonbot.utils.strip_words(message.content, 1).strip()
    if len(game) == 0:
        return "Can't add game: no message provided."

    games = db.get_games()
    time_info = get_next_announcement_info()

    if contains_substring(game, games):
        return f"That game (and {len(games) - 1} other(s)) is already going to be announced at {time_info}."

    db.add_game(game)

    return f"Game added! {len(games) + 1} game(s) will be announced at {time_info}."


@requires_admin
async def get_games(_) -> str:
    """
    Get games

    Returns the list of games to be announced
    """
    games = db.get_games()

    time_info = get_next_announcement_info()

    if len(games) != 0:
        formatted_games = "\n".join(games)
        return f"The following games will be announced at {time_info}:\n{formatted_games}"
    else:
        return f"There are no games to announce so the next announcement at {time_info} will be skipped."


@requires_admin
async def clear_games(_) -> str:
    """
    Clear games

    Clears all games that are being announced
    """
    db.clear_games()
    return "Games cleared!"


def get_next_announcement_info() -> str:
    """
    Get next announcement info

    Returns a string representing the time when the next game announcement will happen.
    Inlcudes the UTC time and duration until that time.
    """
    time_utc = GAME_ANNOUNCE_TIME.strftime("%H:%M UTC")
    remaining = get_delta_to_next_announcement()

    hours, remainder = divmod(remaining.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)

    return f"{time_utc} ({int(hours)}h{int(minutes)}m left)"


def get_delta_to_next_announcement() -> timedelta:
    """
    Get delta to next announcement

    Gets a timedelta to the next announcement time.

    If the current time today is before the configured time, the timedelta will be to the announcement time today.
    Otherwise it will be for the announcement time tomorrow.
    """
    now = datetime.now(timezone.utc)
    announcement = now.replace(hour=GAME_ANNOUNCE_TIME.hour, minute=GAME_ANNOUNCE_TIME.minute)

    if announcement <= now:
        announcement += timedelta(days=1)

    return announcement - now


def contains_substring(target: str, items: list[str]) -> bool:
    """
    contains_substring returns whether target is a substring of any element in items.
    """
    for item in items:
        if target in item:
            return True
    return False
