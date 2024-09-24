import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

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
    xp: int
    monthly_xp: int
    timestamp: datetime

def initialize():
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute("CREATE TABLE IF NOT EXISTS xp (id INT PRIMARY KEY, xp INT, username TEXT, avatar TEXT, monthly INT, month INT, year INT, color TEXT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, title TEXT, response TEXT, img TEXT, flag INT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, command TEXT, FOREIGN KEY(command) REFERENCES commands(name))")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS games (game TEXT)")
    sqlconn.commit()
    sqlconn.close()

def _db_read(query: tuple) -> list[tuple]:
    sqlconn = sqlite3.connect(DB_PATH)
    # The * operator in Python expands a tuple into function params
    results = sqlconn.execute(*query).fetchall()
    sqlconn.close()

    return results

def _db_write(query: tuple[str, list]):
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute(*query)
    sqlconn.commit()
    sqlconn.close()

def fetch_user_data(uid: int) -> UserData:
    query = ("SELECT xp, monthly, month, year FROM xp WHERE id=?", [uid])
    result = _db_read(query)

    curr_time = datetime.now(timezone.utc)
    if len(result) > 0:
        monthly = result[0][1]
        if result[0][2] != curr_time.month or result[0][3] != curr_time.year:
            monthly = 0
        return UserData(uid, result[0][0], monthly, curr_time)
    return UserData(uid, STARTING_XP, STARTING_XP, curr_time)

def set_user_data(user: discord.Member, data: UserData):
    avatar = user.display_avatar.replace(size=64, format="gif", static_format="webp")
    query = ("INSERT OR REPLACE INTO xp (id, xp, username, avatar, monthly, month, year, color) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [user.id, data.xp, str(user), avatar.url, data.monthly_xp, data.timestamp.month, data.timestamp.year, str(user.color)])
    _db_write(query)

def get_leaders() -> list[UserData]:
    curr_time = datetime.now(timezone.utc)
    query = ("SELECT id, xp, monthly FROM xp WHERE username IS NOT NULL ORDER BY xp DESC LIMIT 100",)
    leaders = _db_read(query)
    return [UserData(x[0], x[1], x[2], curr_time) for x in leaders]

def get_monthly_leaders() -> list[UserData]:
    curr_time = datetime.now(timezone.utc)
    query = ("SELECT id, xp, monthly FROM xp WHERE month=? AND year=? AND username IS NOT NULL ORDER BY monthly DESC LIMIT 100", [curr_time.month, curr_time.year])
    leaders = _db_read(query)
    return [UserData(x[0], x[1], x[2], curr_time) for x in leaders]

def prune_leader(uid: int):
    query = ("UPDATE xp SET username = NULL, avatar = NULL, color = NULL WHERE id=?", [uid])
    _db_write(query)

def get_custom_cmds(include_aliases: bool = True) -> dict[str, CommandEntry]:
    query = ("SELECT * FROM commands",)
    cmds = _db_read(query)

    cmd_dict = {}
    for cmd in cmds:
        entry = CommandEntry(cmd[0].lower(), cmd[1], cmd[2], cmd[3], cmd[4])
        cmd_dict[cmd[0].lower()] = entry

    if include_aliases:
        aliases = get_aliases()
        for k, v in aliases.items():
            cmd_dict[k] = cmd_dict[v]

    return cmd_dict

def get_aliases() -> dict[str, str]:
    query = ("SELECT * FROM aliases",)
    aliases = _db_read(query)

    alias_dict = {}
    for alias in aliases:
        alias_dict[alias[0].lower()] = alias[1]
    return alias_dict

def remove_alias(alias: str):
    query = ("DELETE FROM aliases WHERE alias=?", [alias])
    _db_write(query)

def remove_custom_cmd(name: str):
    query = ("DELETE FROM commands WHERE name=?", [name])
    _db_write(query)

    aliases = get_aliases()
    for k, v in aliases.items():
        if v == name:
            remove_alias(k)

def set_new_custom_cmd(name: str, title: str | None, response: str | None, img: str | None, flag: int):
    if response is None and img is None:
        raise InvalidInputError

    query = ("INSERT OR REPLACE INTO commands (name, title, response, img, flag) VALUES (?, ?, ?, ?, ?)", [name, title, response, img, flag])
    _db_write(query)

def set_new_alias(alias: str, command: str):
    query = ("INSERT OR REPLACE INTO aliases (alias, command) VALUES (?, ?)", [alias, command])
    _db_write(query)

def get_rank(userid: int) -> int:
    xp_query = ("SELECT xp FROM xp WHERE id=?", [userid])
    xp_res = _db_read(xp_query)
    xp = 0
    if xp_res:
        xp = xp_res[0][0]

    count_query = ("SELECT COUNT()+1 FROM xp WHERE xp > ? and username IS NOT NULL", [xp])
    results = _db_read(count_query)

    return results[0][0]

def add_game(game: str):
    query = ("INSERT INTO games (game) VALUES (?)", [game])
    _db_write(query)

def get_games() -> list[str]:
    # get games as a list of 1-tuples
    query = ("SELECT game FROM games",)
    raw_results = _db_read(query)

    # convert games into a list of strings
    results = [game[0] for game in raw_results]

    return results

def clear_games():
    query = ("DELETE FROM games", [])
    _db_write(query)
