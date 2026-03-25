import sqlite3
import hashlib
import os
import atexit

# Safe APPDATA handling
appdata = os.environ.get("APPDATA") or os.getcwd()
app_dir = os.path.join(appdata, "BSMS")
os.makedirs(app_dir, exist_ok=True)

def get_saved_db_path(default_path):
    try:
        temp_conn = sqlite3.connect(default_path)
        temp_cursor = temp_conn.cursor()

        temp_cursor.execute("SELECT value FROM settings WHERE key='db_path'")
        row = temp_cursor.fetchone()

        temp_conn.close()

        if row and row[0]:
            return row[0]

    except Exception:
        pass

    return default_path

db_name = os.getenv("DEFAULT_DB_NAME", "bsms.db")
default_db_path = os.path.join(app_dir, db_name)
db_path = get_saved_db_path(default_db_path)

if not os.path.exists(db_path):
    db_path = default_db_path

conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    cursor.execute("""CREATE TABLE IF NOT EXISTS batteries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial TEXT UNIQUE,
    name TEXT,
    brand TEXT,
    capacity TEXT,
    type TEXT,
    purchase_price REAL,
    selling_price REAL,
    quantity INTEGER)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS permissions (
        role TEXT, module TEXT, can_view INTEGER, can_edit INTEGER)""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS battery_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    default_types = ["Tubular", "Solar", "Inverter", "SMF", "Gel"]
    for t in default_types:
        cursor.execute("INSERT OR IGNORE INTO battery_types (name) VALUES (?)", (t,))

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        user TEXT,
        sold_date TEXT,
        paid_date TEXT,
        total REAL,
        paid REAL,
        balance REAL,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        serial TEXT,
        product_name TEXT,
        price REAL,
        quantity INTEGER,
        total REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT UNIQUE,
        email TEXT,
        address TEXT,
        balance REAL DEFAULT 0
    )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY, user TEXT, action TEXT, timestamp TEXT)""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        sale_id INTEGER,
        amount REAL,
        date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
    )
    """)

    # Default admin
    if not cursor.execute("SELECT * FROM users WHERE username='admin'").fetchone():
        cursor.execute("INSERT INTO users VALUES (NULL,?,?,?)",
                       ("admin", hash_password("admin123"), "admin"))

    # Permissions
    defaults = [
        ("admin","inventory",1,1),("admin","sales",1,1),("admin","users",1,1),("admin","customers",1,1),("admin","settings",1,1),
        ("staff","inventory",1,0),("staff","sales",1,1),("staff","customers",1,0)
    ]

    for p in defaults:
        if not cursor.execute("SELECT * FROM permissions WHERE role=? AND module=?", (p[0],p[1])).fetchone():
            cursor.execute("INSERT INTO permissions VALUES (?,?,?,?)", p)

    conn.commit()

init_db()

# Safe close
@atexit.register
def close_connection():
    conn.close()