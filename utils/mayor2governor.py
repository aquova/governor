# A utility script to import the data from Mayor Lewis (.csv) into Governor (SQLite DB)

import csv, sqlite3

DB_PATH="../private/sdv_data.db"
XP_PATH="../private/mayor_lewis_data/sdv_xp.csv"
CMD_PATH="../private/mayor_lewis_data/sdv_custom_commands.csv"

def main():
    # Create DB and tables
    sqlconn = sqlite3.connect(DB_PATH)
    sqlconn.execute("CREATE TABLE IF NOT EXISTS xp (id INT PRIMARY KEY, xp INT);")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS commands (name TEXT, response TEXT);")
    sqlconn.commit()

    # Import XP data
    with open(XP_PATH, newline='') as xpfile:
        xpreader = csv.reader(xpfile, delimiter=',')
        for row in xpreader:
            params = (int(row[0]), int(row[1]))
            sqlconn.execute("INSERT INTO xp (id, xp) VALUES (?, ?);", params)

    sqlconn.commit()

    # Import custom command data
    with open(CMD_PATH, newline='') as cmdfile:
        cmdreader = csv.reader(cmdfile, delimiter=',')
        for row in cmdreader:
            sqlconn.execute("INSERT INTO commands (name, response) VALUES (?, ?);", row)

    sqlconn.commit()
    sqlconn.close()

if __name__ == "__main__":
    main()
