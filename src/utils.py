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
