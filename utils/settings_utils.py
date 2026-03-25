import sqlite3

def is_valid_db(path):
    try:
        test = sqlite3.connect(path)
        cur = test.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        test.close()

        return "users" in tables  # basic validation

    except:
        return False