import sqlite3

from config import settings


def execute_query(sql: str):

    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
