from database import cursor, conn, hash_password
from datetime import datetime

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, hash_password(password)))
    u = cursor.fetchone()
    return {"id":u[0],"username":u[1],"role":u[3]} if u else None

def check_permission(role, module):
    r = cursor.execute("""
        SELECT can_view, can_edit
        FROM permissions
        WHERE role=? AND module=?
    """, (role, module)).fetchone()

    return r if r else (0, 0)

def log_action(user, action):
    cursor.execute("INSERT INTO logs VALUES (NULL,?,?,?)",
                   (user, action, str(datetime.now())))
    conn.commit()

