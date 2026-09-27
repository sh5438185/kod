from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

GENRES = {
    "horror": "😱 Gorkunç",
    "love": "❤️ Söýgi",
    "comedy": "😂 Komediýa",
    "action": "💥 Hereket",
    "drama": "🎭 Drama",
    "fantasy": "🚀 Fantastika",
    "crime": "🔫 Jenaýat",
    "cartoon": "🧸 Multfilm",
}


def genres_keyboard():
    kb = InlineKeyboardBuilder()
    for key, label in GENRES.items():
        kb.button(text=label, callback_data=f"genre:{key}:0")
    kb.adjust(2)
    return kb.as_markup()


def subscribe_keyboard(channels):
    kb = InlineKeyboardBuilder()
    for ch in channels:
        kb.row(InlineKeyboardButton(text=f"📢 {ch['title']}", url=ch["invite_link"]))
    kb.row(InlineKeyboardButton(text="✅ Barladym", callback_data="check_sub"))
    return kb.as_markup()


def genre_pagination_keyboard(genre, offset, has_more):
    kb = InlineKeyboardBuilder()
    row = []
    if offset > 0:
        row.append(InlineKeyboardButton(text="⬅️ Yza", callback_data=f"genre:{genre}:{max(0, offset - 10)}"))
    if has_more:
        row.append(InlineKeyboardButton(text="Öňe ➡️", callback_data=f"genre:{genre}:{offset + 10}"))
    if row:
        kb.row(*row)
    kb.row(InlineKeyboardButton(text="🔙 Žanrlar", callback_data="back_genres"))
    return kb.as_markup()


def movie_deep_link_keyboard(bot_username, code):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎬 Kinony görmek", url=f"https://t.me/{bot_username}?start={code}")
    return kb.as_markup()
