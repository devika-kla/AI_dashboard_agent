#!/usr/bin/env python3
"""
setup.py — One-time setup: downloads Chinook DB and verifies environment.
Run: python setup.py
"""

import os
import sys
import urllib.request
from pathlib import Path

CHINOOK_URL = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
DB_DIR = Path("db")
DB_PATH = DB_DIR / "chinook.db"


def download_chinook():
    if os.path.exists(DB_PATH):
        print(f"✅ {DB_PATH} already exists, skipping download.")
        return
    print(f"⬇️  Downloading Chinook database from GitHub...")
    try:
        urllib.request.urlretrieve(CHINOOK_URL, DB_PATH)
        print(f"✅ Downloaded {DB_PATH} ({os.path.getsize(DB_PATH) // 1024} KB)")
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        print("   Manual download: https://github.com/lerocha/chinook-database")
        sys.exit(1)

def verify_db():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    print(f"✅ Database verified. Tables found: {', '.join(tables)}")

def check_env():
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or key == "sk-your-openai-key-here":
        print("⚠️  OPENAI_API_KEY not set in .env file.")
        print("   Create a .env file and add: OPENAI_API_KEY=sk-...")
    else:
        print(f"✅ OPENAI_API_KEY found (ends in ...{key[-6:]})")

def create_env_file():
    if os.path.exists(".env"):
        print("✅ .env file already exists.")
        return
    with open(".env", "w") as f:
        f.write("OPENAI_API_KEY=sk-your-openai-key-here\n")
        f.write("OPENAI_MODEL=gpt-3.5-turbo\n")
        f.write("DB_PATH=db/chinook.db\n")
        f.write("API_PORT=8000\n")
        f.write("DEBUG=true\n")
    print("✅ Created .env template — add your OpenAI key!")

if __name__ == "__main__":
    print("\n🚀 SQL Agent Setup\n" + "─" * 40)
    download_chinook()
    verify_db()
    create_env_file()
    check_env()
    print("\n✅ Setup complete!")
    print("   Start the API with: python main.py")
    print("   API docs at:        http://localhost:8000/docs\n")
