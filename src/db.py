import sqlite3
from datetime import datetime, timezone
from typing import Optional

from config import DB_PATH, STARTING_XP

"""
Initialize database

Generates database with needed tables if doesn't exist
"""
def initialize():
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute("CREATE TABLE IF NOT EXISTS xp (id INT PRIMARY KEY, xp INT, username TEXT, avatar TEXT, monthly INT, month INT, year INT, color TEXT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, response TEXT, flag INT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS games (game TEXT)")
    sqlconn.commit()
    sqlconn.close()

"""
Database read

Helper function to perform database reads
"""
def _db_read(query: tuple) -> list[tuple]:
    sqlconn = sqlite3.connect(DB_PATH)
    # The * operator in Python expands a tuple into function params
    results = sqlconn.execute(*query).fetchall()
    sqlconn.close()

    return results

"""
Database write

Helper function to perform database writes
"""
def _db_write(query: tuple[str, list]):
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute(*query)
    sqlconn.commit()
    sqlconn.close()

"""
Fetch user XP

Collects the XP database entry for a given user
"""
def fetch_user_xp(user_id: int) -> int:
    query = ("SELECT xp FROM xp WHERE id=?", [user_id])
    found_user = _db_read(query)

    if not found_user:
        return STARTING_XP
    else:
        return found_user[0][0]

"""
Set User XP

Updates a user's XP value, as well as other user information
"""
def set_user_xp(user_id: int, xp: int, user_name: Optional[str], user_avatar: Optional[str], monthly: int, month: int, year: int, color: Optional[str]):
    # We store username and avatar only for the leaderboard
    if user_avatar is None:
        user_avatar = ""

    query = ("REPLACE INTO xp (id, xp, username, avatar, monthly, month, year, color) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [user_id, xp, user_name, user_avatar, monthly, month, year, color])
    _db_write(query)

"""
Fetch user monthly XP

Collects the XP entry for this user for this month
"""
def fetch_user_monthly_xp(user_id: int) -> int:
    query = ("SELECT monthly, month, year FROM xp WHERE id=?", [user_id])
    found_user = _db_read(query)
    curr_time = datetime.now(timezone.utc)

    if found_user == []:
        return 0

    if found_user[0][1] != curr_time.month or found_user[0][2] != curr_time.year:
        return 0
    else:
        return found_user[0][0]

"""
Get leaders

Returns a list of database entries for the top 100 highest XP holders
"""
def get_leaders() -> list[tuple]:
    query = ("SELECT * FROM xp WHERE username IS NOT NULL ORDER BY xp DESC LIMIT 100",)
    leaders = _db_read(query)

    return leaders

"""
Get monthly leaders

Returns a list of database entries for the top 100 highest XP holders this month
"""
def get_monthly_leaders() -> list[tuple]:
    curr_time = datetime.now(timezone.utc)
    query = ("SELECT * FROM xp WHERE month=? AND year=? AND username IS NOT NULL ORDER BY monthly DESC LIMIT 100", [curr_time.month, curr_time.year])
    leaders = _db_read(query)

    return leaders

"""
Get custom commands

Returns the user-set custom commands
"""
def get_custom_cmds() -> dict[str, tuple]:
    query = ("SELECT * FROM commands",)
    cmds = _db_read(query)

    cmd_dict = {}

    for cmd in cmds:
        cmd_dict[cmd[0].lower()] = (cmd[1], cmd[2])

    return cmd_dict

"""
Remove custom command

Removes a previously set custom command from the database
"""
def remove_custom_cmd(name: str):
    query = ("DELETE FROM commands WHERE name=?", [name])
    _db_write(query)

"""
Set new custom command

Adds a new user-defined command to the database
"""
def set_new_custom_cmd(name: str, response: str, flag: int):
    query = ("INSERT OR REPLACE INTO commands (name, response, flag) VALUES (?, ?, ?)", [name, response, flag])
    _db_write(query)

"""
Get rank

Returns the server rank for the user in question
"""
def get_rank(userid: int) -> int:
    xp_query = ("SELECT xp FROM xp WHERE id=?", [userid])
    xp_res = _db_read(xp_query)
    xp = 0
    if xp_res:
        xp = xp_res[0][0]

    count_query = ("SELECT COUNT()+1 FROM xp WHERE xp > ? and username IS NOT NULL", [xp])
    results = _db_read(count_query)

    return results[0][0]

"""
Add game

Adds a new stored game to the database
"""
def add_game(game: str):
    query = ("INSERT INTO games (game) VALUES (?)", [game])
    _db_write(query)

"""
Get games

Gets all games stored
"""
def get_games() -> list[str]:
    # get games as a list of 1-tuples
    query = ("SELECT game FROM games",)
    raw_results = _db_read(query)

    # convert games into a list of strings
    results = [game[0] for game in raw_results]

    return results

"""
Clear games

Removes all currently stored games
"""
def clear_games():
    query = ("DELETE FROM games", [])
    _db_write(query)
