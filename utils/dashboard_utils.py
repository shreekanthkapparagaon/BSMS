from database import cursor

def get_total_products():
    cursor.execute("SELECT COUNT(*) as total FROM batteries")
    return cursor.fetchone()["total"]


def get_type_stats():
    query = """
    SELECT type, COUNT(*) as total_items, SUM(quantity) as total_qty
    FROM batteries
    GROUP BY type
    """
    cursor.execute(query)
    return cursor.fetchall()


def get_low_stock():
    cursor.execute("SELECT COUNT(*) as low FROM batteries WHERE quantity < 5")
    return cursor.fetchone()["low"]