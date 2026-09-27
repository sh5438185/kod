import sqlite3
from contextlib import closing

from config import DB_PATH, CHANNEL_USERNAME, CHANNEL_URL, DEFAULT_LANG


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(_connect()) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            year TEXT,
            country TEXT,
            genre TEXT,
            description TEXT,
            file_id TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'video'
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            title TEXT,
            invite_link TEXT
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT NOT NULL DEFAULT 'tr',
            first_name TEXT
        )""")
        conn.commit()

        # Majburiy obuna kanali standart bo'lib bazaga qo'shiladi (agar hali yo'q bo'lsa)
        cur = conn.execute("SELECT COUNT(*) AS c FROM channels")
        if cur.fetchone()["c"] == 0:
            conn.execute(
                "INSERT OR IGNORE INTO channels (chat_id, title, invite_link) VALUES (?,?,?)",
                (CHANNEL_USERNAME, "Filmlar", CHANNEL_URL),
            )
            conn.commit()


# ---------- USERS / LANG ----------

def set_user(user_id: int, lang: str, first_name: str = None):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO users (user_id, lang, first_name) VALUES (?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang, first_name=excluded.first_name",
            (user_id, lang, first_name),
        )
        conn.commit()


def get_user_lang(user_id: int, default: str = DEFAULT_LANG) -> str:
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return row["lang"] if row else default


def count_users() -> int:
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT COUNT(*) AS c FROM users")
        return cur.fetchone()["c"]


# ---------- MOVIES ----------

def add_movie(code, title, year, country, genre, description, file_id, content_type="video"):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT INTO movies (code, title, year, country, genre, description, file_id, content_type) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (code, title, year, country, genre, description, file_id, content_type),
        )
        conn.commit()


def get_movie_by_code(code):
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT * FROM movies WHERE code=?", (code,))
        return cur.fetchone()


def delete_movie(code):
    with closing(_connect()) as conn:
        cur = conn.execute("DELETE FROM movies WHERE code=?", (code,))
        conn.commit()
        return cur.rowcount > 0


def get_movies_by_genre(genre, limit=10, offset=0):
    with closing(_connect()) as conn:
        cur = conn.execute(
            "SELECT * FROM movies WHERE genre=? ORDER BY id DESC LIMIT ? OFFSET ?",
            (genre, limit, offset),
        )
        return cur.fetchall()


def count_movies_by_genre(genre):
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT COUNT(*) AS c FROM movies WHERE genre=?", (genre,))
        return cur.fetchone()["c"]


def count_movies():
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT COUNT(*) AS c FROM movies")
        return cur.fetchone()["c"]


def search_movies_by_title(query, limit=15):
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT * FROM movies WHERE title LIKE ? LIMIT ?", (f"%{query}%", limit))
        return cur.fetchall()


# ---------- CHANNELS ----------

def add_channel(chat_id, title, invite_link):
    with closing(_connect()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO channels (chat_id, title, invite_link) VALUES (?,?,?)",
            (chat_id, title, invite_link),
        )
        conn.commit()


def remove_channel(chat_id):
    with closing(_connect()) as conn:
        cur = conn.execute("DELETE FROM channels WHERE chat_id=?", (chat_id,))
        conn.commit()
        return cur.rowcount > 0


def get_channels():
    with closing(_connect()) as conn:
        cur = conn.execute("SELECT * FROM channels")
        return cur.fetchall()
