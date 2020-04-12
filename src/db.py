import sqlite3
from config import DB_PATH

"""
Fetch user XP

Collects the XP database entry for a given user

Input: user_id - User ID in question - int
"""
def fetch_user_xp(user_id):
    sqlconn = sqlite3.connect(DB_PATH)

    foundUser = sqlconn.execute("SELECT xp FROM xp WHERE id=?", [user_id]).fetchall()

    sqlconn.close()

    if foundUser == []:
        return None
    else:
        return foundUser[0][0]

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
    sqlconn = sqlite3.connect(DB_PATH)

    # We store username and avatar only for the leaderboard
    if user_avatar == None:
        user_avatar = ""
    sqlconn.execute("REPLACE INTO xp (id, xp, username, avatar) VALUES (?, ?, ?, ?)", [user_id, xp, user_name, user_avatar])

    sqlconn.commit()
    sqlconn.close()

"""
Get leaders

Returns a list of database entries for the top 100 highest XP holders
"""
def get_leaders():
    sqlconn = sqlite3.connect(DB_PATH)

    leaders = sqlconn.execute("SELECT * FROM xp ORDER BY xp DESC LIMIT 100").fetchall()

    sqlconn.close()

    return leaders

"""
Get custom commands

Returns the user-set custom commands
"""
def get_custom_cmds():
    sqlconn = sqlite3.connect(DB_PATH)

    cmds = sqlconn.execute("SELECT * FROM commands").fetchall()

    sqlconn.close()

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
    sqlconn = sqlite3.connect(DB_PATH)

    sqlconn.execute("DELETE FROM commands WHERE name=?", [name])

    sqlconn.commit()
    sqlconn.close()

"""
Set new custom command

Adds a new user-defined command to the database

Inputs:
    - name - How to invoke the command - str
    - response - Reply upon successful invocation - str
"""
def set_new_custom_cmd(name, response):
    sqlconn = sqlite3.connect(DB_PATH)

    sqlconn.execute("REPLACE INTO commands (name, response) VALUES (?, ?)", [name, response])

    sqlconn.commit()
    sqlconn.close()

def get_rank(userid):
    sqlconn = sqlite3.connect(DB_PATH)

    results = sqlconn.execute("SELECT COUNT()+1 FROM xp WHERE xp > (SELECT xp FROM xp WHERE id=?)", [userid]).fetchone()

    sqlconn.close()

    if results == []:
        return None

    return results[0]
