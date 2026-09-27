from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts import GENRES, genre_label, t


def language_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇹🇷 Türkçe", callback_data="lang:tr")
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.adjust(2)
    return kb.as_markup()


def genres_keyboard(lang: str):
    kb = InlineKeyboardBuilder()
    for key in GENRES:
        kb.button(text=genre_label(key, lang), callback_data=f"genre:{key}:0")
    kb.adjust(2)
    return kb.as_markup()


def subscribe_keyboard(channels, lang: str):
    kb = InlineKeyboardBuilder()
    for ch in channels:
        title = ch["title"] or ch["chat_id"]
        kb.row(InlineKeyboardButton(text=t(lang, "subscribe_channel_btn", title=title), url=ch["invite_link"]))
    kb.row(InlineKeyboardButton(text=t(lang, "check_sub_btn"), callback_data="check_sub"))
    return kb.as_markup()


def genre_pagination_keyboard(genre, offset, has_more, lang: str):
    kb = InlineKeyboardBuilder()
    row = []
    if offset > 0:
        row.append(InlineKeyboardButton(text=t(lang, "prev_btn"), callback_data=f"genre:{genre}:{max(0, offset - 10)}"))
    if has_more:
        row.append(InlineKeyboardButton(text=t(lang, "next_btn"), callback_data=f"genre:{genre}:{offset + 10}"))
    if row:
        kb.row(*row)
    kb.row(InlineKeyboardButton(text=t(lang, "back_genres_btn"), callback_data="back_genres"))
    return kb.as_markup()


def movie_deep_link_keyboard(bot_username, code, lang: str = "tr"):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "watch_btn"), url=f"https://t.me/{bot_username}?start={code}")
    return kb.as_markup()


# ---------- ADMIN ----------

def admin_panel_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Kino qo'shish", callback_data="adm:add")
    kb.button(text="🗑 Kino o'chirish", callback_data="adm:del")
    kb.button(text="📊 Statistika", callback_data="adm:stats")
    kb.button(text="📋 Kanallar", callback_data="adm:channels")
    kb.adjust(2)
    return kb.as_markup()


def admin_genre_choice_keyboard():
    kb = InlineKeyboardBuilder()
    for key in GENRES:
        kb.button(text=f"{genre_label(key, 'tr')} / {genre_label(key, 'ru')}", callback_data=f"admgenre:{key}")
    kb.adjust(1)
    return kb.as_markup()


def admin_cancel_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Bekor qilish", callback_data="adm:cancel")
    return kb.as_markup()


def channels_manage_keyboard(channels):
    kb = InlineKeyboardBuilder()
    for ch in channels:
        kb.row(InlineKeyboardButton(
            text=f"🗑 {ch['title'] or ch['chat_id']}",
            callback_data=f"admchdel:{ch['chat_id']}",
        ))
    kb.row(InlineKeyboardButton(text="🔙 Admin panel", callback_data="adm:back"))
    return kb.as_markup()
