import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        points INTEGER DEFAULT 1,
        join_verified BOOLEAN DEFAULT 0,
        redeemed_codes TEXT DEFAULT '[]'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS gift_codes (
        code TEXT PRIMARY KEY,
        points INTEGER,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "first_name": row[1], "username": row[2], "points": row[3], "join_verified": row[4], "redeemed_codes": json.loads(row[5])}
    return None

def create_user(user_id, first_name, username):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, first_name, username) VALUES (?, ?, ?)", (user_id, first_name, username))
    conn.commit()
    conn.close()

def update_points(user_id, points):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()

def verify_user(user_id):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET join_verified = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
