import sqlite3
from config import DB_PATH

def fetch_user_xp(user_id):
    sqlconn = sqlite3.connect(DB_PATH)

    foundUser = sqlconn.execute("SELECT xp FROM xp WHERE id=?", [user_id]).fetchall()

    sqlconn.close()

    if foundUser == []:
        return None
    else:
        return foundUser[0][0]

def set_user_xp(user_id, xp):
    sqlconn = sqlite3.connect(DB_PATH)

    sqlconn.execute("REPLACE INTO xp (id, xp) VALUES (?, ?)", [user_id, xp])

    sqlconn.commit()
    sqlconn.close()

def get_custom_cmds():
    sqlconn = sqlite3.connect(DB_PATH)

    cmds = sqlconn.execute("SELECT * FROM commands").fetchall()

    sqlconn.close()

    cmd_dict = {}

    for cmd in cmds:
        cmd_dict[cmd[0].upper()] = cmd[1]

    return cmd_dict

def set_new_custom_cmd(name, response):
    sqlconn = sqlite3.connect(DB_PATH)

    sqlconn.execute("REPLACE INTO commands (name, response) VALUES (?, ?)", [name, response])

    sqlconn.commit()
    sqlconn.close()
