import sqlite3

from config import settings


def get_schema():

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)
    tables = cursor.fetchall()

    schema_text = ""
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        schema_text += f"\nTABLE: {table_name}\n"
        for col in columns:
            schema_text += f"- {col[1]} ({col[2]})\n"

    conn.close()
    return schema_text
