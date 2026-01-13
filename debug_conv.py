import sqlite3
import json
import os
from pathlib import Path

db_path = Path("~/.agent_data/conversations/agent.db").expanduser()

if not db_path.exists():
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get latest messages
cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

print("--- LATEST MESSAGES ---")
for row in rows:
    print(f"ID: {row['id']} | Role: {row['role']}")
    print(f"Content: {row['content'][:100]}...")
    if row['tool_calls']:
        print(f"Tool Calls: {row['tool_calls']}")
    print("-" * 20)

conn.close()
