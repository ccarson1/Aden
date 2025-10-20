# auth_db.py
import sqlite3
import time
import uuid
import os
import bcrypt

DB_FILE = os.path.join(os.path.dirname(__file__), "auth.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    # Characters table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        char_name TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    # Tokens table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS player_data (
        player_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        x REAL NOT NULL,
        y REAL NOT NULL,
        direction TEXT NOT NULL,
        current_map TEXT,
        z_index INTEGER DEFAULT 0,
        last_update INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def create_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        # Hash the password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        hashed = row[0]
        # Compare hashed password
        return bcrypt.checkpw(password.encode(), hashed)
    return False


def create_character(username, char_name):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return False
    user_id = user[0]
    cur.execute("INSERT INTO characters (user_id, char_name) VALUES (?, ?)", (user_id, char_name))
    conn.commit()
    conn.close()
    return True


# ---------------- Token Functions ----------------
TOKEN_TTL = 3600  # 1 hour

def create_token(username):
    token = str(uuid.uuid4())
    now = int(time.time())
    expires = now + TOKEN_TTL
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tokens (token, username, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token, username, now, expires)
    )
    conn.commit()
    conn.close()
    return token


def get_token(username):
    """Return existing valid token or create a new one"""
    now = int(time.time())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT token, expires_at FROM tokens WHERE username=? ORDER BY expires_at DESC LIMIT 1",
        (username,)
    )
    row = cur.fetchone()
    if row and row[1] > now:
        conn.close()
        return row[0]
    # else, create new token
    conn.close()
    return create_token(username)


def verify_token(token):
    now = int(time.time())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT username, expires_at FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    conn.close()
    if row and row[1] > now:
        return True, row[0]  # valid, return username
    return False, None

def cleanup_expired_tokens():
    """Remove tokens from the database that have expired."""
    now = int(time.time())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM tokens WHERE expires_at <= ?", (now,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted


def refresh_token(token, additional_ttl=TOKEN_TTL):
    """
    Extend the token's expiration if it's still valid.
    Returns True if refreshed, False if token is invalid/expired.
    """
    now = int(time.time())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Check if token exists and is still valid
    cur.execute("SELECT expires_at FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    if not row or row[0] <= now:
        conn.close()
        return False

    # Update expiration
    new_expires = now + additional_ttl
    cur.execute("UPDATE tokens SET expires_at=? WHERE token=?", (new_expires, token))
    conn.commit()
    conn.close()
    return True


def save_player_state(player_id, username, x, y, direction, current_map, z_index):
    now = int(time.time())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO player_data (player_id, username, x, y, direction, current_map, z_index, last_update)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(player_id) DO UPDATE SET
        x=excluded.x,
        y=excluded.y,
        direction=excluded.direction,
        current_map=excluded.current_map,
        z_index=excluded.z_index,
        last_update=excluded.last_update
    """, (player_id, username, x, y, direction, current_map, z_index, now))
    conn.commit()
    conn.close()

def load_player_state(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT x, y, direction, current_map, z_index FROM player_data WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "x": row[0],
            "y": row[1],
            "direction": row[2],
            "current_map": row[3],
            "z_index": row[4]
        }
    return {"x": 100, "y": 100, "direction": "down", "current_map": "Test_01", "z_index": 0}

def get_username_from_token(token):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT username FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None
