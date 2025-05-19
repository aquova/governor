# pyright: reportCallInDefaultInitializer=false, reportExplicitAny=false

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import discord

from config import DB_PATH, STARTING_XP
from err import InvalidInputError

@dataclass
class CommandEntry:
    name: str
    title: str | None
    response: str | None
    img: str | None
    flags: int

@dataclass
class UserData:
    uid: int
    total_xp: int
    monthly_xp: int
    weekly_xp: int
    timestamp: datetime

def initialize():
    """
    Database initialize

    Database initialization, runs at bot startup
    """
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute("CREATE TABLE IF NOT EXISTS xp (id INT PRIMARY KEY, xp INT, username TEXT, avatar TEXT, monthly INT, month INT, weekly INT, week INT, color TEXT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS yappers (FOREIGN KEY(id) REFERENCES xp(id), week INT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, title TEXT, response TEXT, img TEXT, flag INT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, command TEXT, FOREIGN KEY(command) REFERENCES commands(name))")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS games (game TEXT)")
    sqlconn.commit()
    sqlconn.close()

def _db_read(query: str, params: list[Any] = []) -> list[tuple[Any, ...]]:
    """
    Database read

    Helper function to handle database reads

    `query` needs to be a tuple object, even if the query has no parameters it should be a tuple of one
    """
    sqlconn = sqlite3.connect(DB_PATH)
    results = sqlconn.execute(query, params).fetchall()
    sqlconn.close()

    return results

def _db_write(query: str, params: list[Any] = []):
    """
    Database write

    Helper function to handle database writes

    `query` needs to be a tuple object, even if the query has no parameters it should be a tuple of one
    """
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute(query, params)
    sqlconn.commit()
    sqlconn.close()

def get_month(dt: datetime) -> int:
    """
    Get month

    Converts a datetime object into a month index value
    """
    return 12 * (dt.year - 2000) + dt.month - 1

def get_week(dt: datetime) -> int:
    """
    Get week

    Converts a datetime object into a weekly index value
    """
    week = int(dt.strftime("%V"))
    return 52 * (dt.year - 2000) + week

def fetch_user_data(uid: int) -> UserData:
    """
    Fetch user data

    Returns the stored data about a user, given a user id
    """
    query = "SELECT xp, monthly, month, weekly, week FROM xp WHERE id=?"
    result: list[tuple[int, int, int, int, int]] = _db_read(query, [uid])

    curr_time = datetime.now(timezone.utc)
    curr_month = get_month(curr_time)
    curr_week = get_week(curr_time)

    if len(result) > 0:
        total = result[0][0]
        monthly = result[0][1]
        month_idx = result[0][2]
        if month_idx != curr_month:
            monthly = 0

        weekly = result[0][3]
        week_idx = result[0][4]
        if week_idx != curr_week:
            weekly = 0

        return UserData(uid, total, monthly, weekly, curr_time)
    return UserData(uid, STARTING_XP, STARTING_XP, STARTING_XP, curr_time)

def set_user_data(user: discord.Member, data: UserData):
    """
    Set user data

    Saves the UserData object into the database
    """
    avatar = user.display_avatar.replace(size=64, format="gif", static_format="webp")
    query = "INSERT OR REPLACE INTO xp (id, xp, username, avatar, monthly, month, weekly, week, color) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    _db_write(
        query,
        [
            user.id,
            data.total_xp,
            str(user),
            avatar.url,
            data.monthly_xp,
            get_month(data.timestamp),
            data.weekly_xp,
            get_week(data.timestamp),
            str(user.color)
        ]
    )

def get_leaders() -> list[UserData]:
    """
    Get Leaders

    Returns the top 100 global XP leaders, that haven't been hidden for inactivity
    """
    query = "SELECT id, xp, monthly, month, weekly, week FROM xp WHERE username IS NOT NULL ORDER BY xp DESC LIMIT 100"
    leaders: list[tuple[int, int, int, int, int, int]] = _db_read(query)

    ret: list[UserData] = []
    curr_time = datetime.now(timezone.utc)
    curr_month = get_month(curr_time)
    curr_week = get_week(curr_time)
    for leader in leaders:
        monthly = leader[2]
        if leader[3] != curr_month:
            monthly = 0

        weekly = leader[4]
        if leader[5] != curr_week:
            weekly = 0
        ret.append(UserData(leader[0], leader[1], monthly, weekly, curr_time))
    return ret

def get_monthly_leaders() -> list[UserData]:
    """
    Get monthly leaders

    Returns the top 100 monthly leaders for the current month
    """
    curr_time = datetime.now(timezone.utc)
    query = "SELECT id, xp, monthly, weekly FROM xp WHERE month=? AND username IS NOT NULL ORDER BY monthly DESC LIMIT 100"
    leaders: list[tuple[int, int, int, int]] = _db_read(query, [get_month(curr_time)])
    return [UserData(x[0], x[1], x[2], x[3], curr_time) for x in leaders]

def get_weekly_leaders() -> list[UserData]:
    """
    Get weekly leaders

    Returns the top 100 weekly leaders for the current week
    """
    curr_time = datetime.now(timezone.utc)
    query = "SELECT id, xp, monthly, weekly FROM xp WHERE week=? AND username IS NOT NULL ORDER BY weekly DESC LIMIT 100"
    leaders: list[tuple[int, int, int, int]] = _db_read(query, [get_week(curr_time)])
    return [UserData(x[0], x[1], x[2], x[3], curr_time) for x in leaders]

def add_yapper(uid: int, week: int):
    """
    Add Yapper

    Adds a weekly yapper winner to the database
    """
    query = "INSERT OR REPLACE INTO yappers (id, week) VALUES (?, ?)"
    _db_write(query, [uid, week])

def get_old_yappers(week: int) -> list[int]:
    """
    Get Old Yappers

    Gets the list of IDs for users who were the most talkative in the given week

    The input week should be formatted with the `get_week` function
    """
    query = "SELECT id FROM yappers WHERE week=?"
    result: list[tuple[int]] = _db_read(query, [week])
    return [x[0] for x in result]

def get_last_yapper_victory(uid: int) -> int | None:
    """
    Get Last Yapper Victory

    Gets the week the given user was last a weekly talking winner

    Returns a week formatted in the same fashion as the `get_week` function
    """
    query = "SELECT week FROM yappers WHERE id=?"
    result: list[tuple[int]] = _db_read(query, [uid])
    if len(result) > 0:
        return result[0][0]
    return None

def prune_leader(uid: int):
    """
    Prune Leader

    Marks a user as ineligable for the leaderboard by setting their username, avatar, and color blank
    """
    query = "UPDATE xp SET username = NULL, avatar = NULL, color = NULL WHERE id=?"
    _db_write(query, [uid])

def get_custom_cmds(include_aliases: bool = True) -> dict[str, CommandEntry]:
    """
    Get Custom Commands

    Returns all the custom commands as a dictionary

    Dictionary maps command name to their response, including metadata
    """
    query = "SELECT * FROM commands"
    cmds: list[tuple[str, str, str, str, int]] = _db_read(query)

    cmd_dict: dict[str, CommandEntry] = {}
    for cmd in cmds:
        entry = CommandEntry(cmd[0].lower(), cmd[1], cmd[2], cmd[3], cmd[4])
        cmd_dict[cmd[0].lower()] = entry

    if include_aliases:
        aliases = get_aliases()
        for k, v in aliases.items():
            cmd_dict[k] = cmd_dict[v]

    return cmd_dict

def get_aliases() -> dict[str, str]:
    """
    Get aliases

    Returns a dictionary mapping all aliases to their canonical command

    If a command has more than one alias, then each alias is a separate entry
    """
    query = "SELECT * FROM aliases"
    aliases: list[tuple[str, str, str]] = _db_read(query)

    alias_dict: dict[str, str] = {}
    for alias in aliases:
        alias_dict[alias[0].lower()] = alias[1]
    return alias_dict

def remove_alias(alias: str):
    """
    Remove alias

    Removes a command alias from the database
    """
    query = "DELETE FROM aliases WHERE alias=?"
    _db_write(query, [alias])

def remove_custom_cmd(name: str):
    """
    Remove custom command

    Removes a custom command and all its aliases from the database
    """
    query = "DELETE FROM commands WHERE name=?"
    _db_write(query, [name])

    aliases = get_aliases()
    for k, v in aliases.items():
        if v == name:
            remove_alias(k)

def set_new_custom_cmd(name: str, title: str | None, response: str | None, img: str | None, flag: int):
    """
    Set new custom command

    Adds a new custom command

    While response and image are both optional, there must be at least one defined, otherwise it will throw an InvalidInputError
    """
    if response is None and img is None:
        raise InvalidInputError

    query = "INSERT OR REPLACE INTO commands (name, title, response, img, flag) VALUES (?, ?, ?, ?, ?)"
    _db_write(query, [name, title, response, img, flag])

def set_new_alias(alias: str, command: str):
    """
    Set new alias

    Sets a new alias for the existing command
    """
    query = "INSERT OR REPLACE INTO aliases (alias, command) VALUES (?, ?)"
    _db_write(query, [alias, command])

def get_rank(uid: int) -> int:
    """
    Get rank

    Returns the rank the user of the given ID is on the leaderboard
    """
    xp_query = "SELECT xp FROM xp WHERE id=?"
    xp_res: list[tuple[int]] = _db_read(xp_query, [uid])
    xp = 0
    if xp_res:
        xp = xp_res[0][0]

    count_query = "SELECT COUNT()+1 FROM xp WHERE xp > ? and username IS NOT NULL"
    results: list[tuple[int]] = _db_read(count_query, [xp])

    return results[0][0]

def add_game(game: str):
    """
    Add game

    Adds a URL for a video game giveaway into the database
    """
    query = "INSERT INTO games (game) VALUES (?)"
    _db_write(query, [game])

def get_games() -> list[str]:
    """
    Get games

    Gets a list of games giveaways to be posted in chat
    """
    query = "SELECT game FROM games"
    raw_results: list[tuple[str]] = _db_read(query)
    results = [game[0] for game in raw_results]
    return results

def clear_games():
    """
    Clear games

    Deletes all the games from the upcoming game giveaway post
    """
    query = "DELETE FROM games"
    _db_write(query)
