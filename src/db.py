import sqlite3
from config import DB_PATH

"""
Initialize database

Generates database with needed tables if doesn't exist
"""
def initialize():
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute("CREATE TABLE IF NOT EXISTS xp (id INT PRIMARY KEY, xp INT, username TEXT, avatar TEXT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS commands (name TEXT PRIMARY KEY, response TEXT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS games (game TEXT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS raffle (id INT, channel INT)")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS hunters (id INT PRIMARY KEY, username TEXT, count INT)")
    sqlconn.commit()
    sqlconn.close()

"""
Database read

Helper function to perform database reads
"""
def _db_read(query):
    sqlconn = sqlite3.connect(DB_PATH)
    # The * operator in Python expands a tuple into function params
    results = sqlconn.execute(*query).fetchall()
    sqlconn.close()

    return results

"""
Database write

Helper function to perform database writes
"""
def _db_write(query):
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute(*query)
    sqlconn.commit()
    sqlconn.close()

"""
Fetch user XP

Collects the XP database entry for a given user

Input: user_id - User ID in question - int
"""
def fetch_user_xp(user_id):
    query = ("SELECT xp FROM xp WHERE id=?", [user_id])
    found_user = _db_read(query)

    if found_user == []:
        return 0
    else:
        return found_user[0][0]

"""
Set User XP

Updates a user's XP value, as well as other user information

Inputs:
    - user_id - The user's ID - int
    - xp - User's XP tally - int
    - user_name - User's name, formatted as username#1234 - str
    - user_avatar - Hash for user's avatar image, used in the URL - str
"""
def set_user_xp(user_id, xp, user_name, user_avatar):
    # We store username and avatar only for the leaderboard
    if user_avatar == None:
        user_avatar = ""

    query = ("REPLACE INTO xp (id, xp, username, avatar) VALUES (?, ?, ?, ?)", [user_id, xp, user_name, user_avatar])
    _db_write(query)

"""
Get leaders

Returns a list of database entries for the top 100 highest XP holders
"""
def get_leaders():
    query = ("SELECT * FROM xp ORDER BY xp DESC LIMIT 100",)
    leaders = _db_read(query)

    return leaders

"""
Get custom commands

Returns the user-set custom commands
"""
def get_custom_cmds():
    query = ("SELECT * FROM commands",)
    cmds = _db_read(query)

    cmd_dict = {}

    for cmd in cmds:
        cmd_dict[cmd[0]] = cmd[1]

    return cmd_dict

"""
Remove custom command

Removes a previously set custom command from the database

Input: name - Name of custom command - str
"""
def remove_custom_cmd(name):
    query = ("DELETE FROM commands WHERE name=?", [name])
    _db_write(query)

"""
Set new custom command

Adds a new user-defined command to the database

Inputs:
    - name - How to invoke the command - str
    - response - Reply upon successful invocation - str
"""
def set_new_custom_cmd(name, response):
    query = ("INSERT OR REPLACE INTO commands (name, response) VALUES (?, ?)", [name, response])
    _db_write(query)

"""
Get rank

Returns the server rank for the user in question
"""
def get_rank(userid):
    xp_query = ("SELECT xp FROM xp WHERE id=?", [userid])
    xp_res = _db_read(xp_query)
    if xp_res == []:
        xp = 0
    else:
        xp = xp_res[0][0]

    count_query = ("SELECT COUNT()+1 FROM xp WHERE xp > ? and username IS NOT NULL", [xp])
    results = _db_read(count_query)

    return results[0][0]

"""
Add game

Adds a new stored game to the database

Inputs:
    - game - A link to the game plus any additional info about the game - str
"""
def add_game(game):
    query = ("INSERT INTO games (game) VALUES (?)", [game])
    _db_write(query)

"""
Get games

Gets all games stored
"""
def get_games():
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
    query = ("DELETE FROM games",)
    _db_write(query)

"""
Add to raffle

Adds a user's ID to the event raffle
"""
def add_raffle(userid, chanid):
    read_query = ("SELECT id FROM raffle WHERE id=? AND channel=?", [userid, chanid])
    results = _db_read(read_query)
    if results == []:
        write_query = ("INSERT INTO raffle (id, channel) VALUES (?, ?)", [userid, chanid])
        _db_write(write_query)
        return True

    return False

"""
Increment hunter

Increments the number successful Hunts a user has had
"""
def inc_hunter(userid, username):
    read_query = ("SELECT count FROM hunters WHERE id=?", [userid])
    user_cnt = _db_read(read_query)
    try:
        cnt = user_cnt[0][0] + 1
    except IndexError:
        cnt = 1

    write_query = ("REPLACE INTO hunters (id, username, count) VALUES (?, ?, ?)", [userid, username, cnt])
    _db_write(write_query)

def get_hunters():
    read_query = ("SELECT * FROM hunters",)
    hunters = _db_read(read_query)
    return hunters
