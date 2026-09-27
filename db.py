import sqlite3
from contextlib import closing

from config import DB_PATH


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            year TEXT,
            country TEXT,
            genre TEXT,
            description TEXT,
            file_id TEXT NOT NULL
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            title TEXT,
            invite_link TEXT
        )""")
        conn.commit()


def add_movie(code, title, year, country, genre, description, file_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO movies (code, title, year, country, genre, description, file_id) "
            "VALUES (?,?,?,?,?,?,?)",
            (code, title, year, country, genre, description, file_id),
        )
        conn.commit()


def get_movie_by_code(code):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM movies WHERE code=?", (code,))
        return cur.fetchone()


def delete_movie(code):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("DELETE FROM movies WHERE code=?", (code,))
        conn.commit()
        return cur.rowcount > 0


def get_movies_by_genre(genre, limit=10, offset=0):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM movies WHERE genre=? ORDER BY id DESC LIMIT ? OFFSET ?",
            (genre, limit, offset),
        )
        return cur.fetchall()


def count_movies_by_genre(genre):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM movies WHERE genre=?", (genre,))
        return cur.fetchone()[0]


def search_movies_by_title(query, limit=15):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM movies WHERE title LIKE ? LIMIT ?", (f"%{query}%", limit))
        return cur.fetchall()


def add_channel(chat_id, title, invite_link):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO channels (chat_id, title, invite_link) VALUES (?,?,?)",
            (chat_id, title, invite_link),
        )
        conn.commit()


def remove_channel(chat_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("DELETE FROM channels WHERE chat_id=?", (chat_id,))
        conn.commit()
        return cur.rowcount > 0


def get_channels():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM channels")
        return cur.fetchall()
