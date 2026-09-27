import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
)

from config import BOT_TOKEN, ADMIN_IDS
import db
from keyboards import (
    GENRES, genres_keyboard, subscribe_keyboard,
    genre_pagination_keyboard, movie_deep_link_keyboard,
)

logging.basicConfig(level=logging.INFO)

router = Router()
pending_start = {}  # user_id -> code (obuna bolandan soň ugradylýan kino kody)


class AddMovie(StatesGroup):
    code = State()
    title = State()
    year = State()
    country = State()
    genre = State()
    description = State()
    video = State()


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    channels = db.get_channels()
    if not channels:
        return True
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["chat_id"], user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False
    return True


def movie_caption(movie) -> str:
    return (
        f"🎬 <b>{movie['title']}</b>\n"
        f"📅 Ýyl: {movie['year']}\n"
        f"🌍 Ýurt: {movie['country']}\n"
        f"🎭 Žanr: {GENRES.get(movie['genre'], movie['genre'])}\n\n"
        f"📝 {movie['description']}\n\n"
        f"🔑 Kod: <code>{movie['code']}</code>"
    )


async def send_movie(bot: Bot, chat_id: int, code: str):
    movie = db.get_movie_by_code(code)
    if not movie:
        await bot.send_message(chat_id, "❌ Bu kod boýunça kino tapylmady.")
        return
    await bot.send_video(chat_id, movie["file_id"], caption=movie_caption(movie), parse_mode="HTML")


# ---------- USER ----------

@router.message(CommandStart())
async def cmd_start(message: Message, command, bot: Bot):
    args = command.args
    if not await is_subscribed(bot, message.from_user.id):
        if args:
            pending_start[message.from_user.id] = args
        channels = db.get_channels()
        await message.answer(
            "👋 Salam! Botdan peýdalanmak üçin ilki aşakdaky kanal(lar)a agza bolmaly:",
            reply_markup=subscribe_keyboard(channels),
        )
        return
    if args:
        await send_movie(bot, message.chat.id, args)
        return
    await message.answer(
        "👋 Salam!\n\nMenden kino gözläp bilersiň:\n"
        "🔑 Kino kodyny ýazyp iber\n"
        "🎭 Ýa-da aşakdaky žanrlardan birini saýla\n"
        "🔍 Islendik çatda @bot_ady ýazyp kino ady bilen hem gözläp bilersiň",
        reply_markup=genres_keyboard(),
    )


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        code = pending_start.pop(callback.from_user.id, None)
        await callback.message.delete()
        if code:
            await send_movie(bot, callback.message.chat.id, code)
        else:
            await callback.message.answer(
                "✅ Sag bol! Indi kino kodyny ýaz ýa-da žanr saýla:",
                reply_markup=genres_keyboard(),
            )
    else:
        await callback.answer("❌ Entek ähli kanallara agza bolmadyň!", show_alert=True)


@router.callback_query(F.data == "back_genres")
async def cb_back_genres(callback: CallbackQuery):
    await callback.message.edit_text("🎭 Žanr saýla:", reply_markup=genres_keyboard())


@router.callback_query(F.data.startswith("genre:"))
async def cb_genre(callback: CallbackQuery):
    _, genre, offset = callback.data.split(":")
    offset = int(offset)
    movies = db.get_movies_by_genre(genre, limit=10, offset=offset)
    total = db.count_movies_by_genre(genre)
    if not movies:
        await callback.answer("😔 Bu žanrda entek kino ýok.", show_alert=True)
        return
    text = f"{GENRES.get(genre, genre)} žanrdaky kinolar:\n\n"
    text += "\n".join(f"🔑 <code>{m['code']}</code> — {m['title']} ({m['year']})" for m in movies)
    has_more = offset + 10 < total
    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=genre_pagination_keyboard(genre, offset, has_more),
    )


@router.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def msg_code_search(message: Message, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        channels = db.get_channels()
        await message.answer("❗️ Ilki kanal(lar)a agza bol:", reply_markup=subscribe_keyboard(channels))
        return
    code = message.text.strip()
    movie = db.get_movie_by_code(code)
    if movie:
        await bot.send_video(message.chat.id, movie["file_id"], caption=movie_caption(movie), parse_mode="HTML")
        return
    results = db.search_movies_by_title(code)
    if results:
        text = "🔍 Tapylan kinolar:\n\n" + "\n".join(
            f"🔑 <code>{m['code']}</code> — {m['title']} ({m['year']})" for m in results
        )
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("❌ Hiç zat tapylmady. Kody ýa-da ady dogry ýazandygyňy barla.")


@router.inline_query()
async def inline_search(inline_query: InlineQuery, bot: Bot):
    query = inline_query.query.strip()
    if not query:
        await inline_query.answer([], cache_time=1)
        return
    movies = db.search_movies_by_title(query)
    me = await bot.get_me()
    results = []
    for m in movies[:15]:
        results.append(
            InlineQueryResultArticle(
                id=m["code"],
                title=f"{m['title']} ({m['year']})",
                description=f"{GENRES.get(m['genre'], m['genre'])} | {m['country']}",
                input_message_content=InputTextMessageContent(
                    message_text=movie_caption(m), parse_mode="HTML"
                ),
                reply_markup=movie_deep_link_keyboard(me.username, m["code"]),
            )
        )
    await inline_query.answer(results, cache_time=1, is_personal=True)


# ---------- ADMIN ----------

def admin_only(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS


@router.message(Command("addmovie"))
async def admin_add_start(message: Message, state: FSMContext):
    if not admin_only(message):
        return
    await state.set_state(AddMovie.code)
    await message.answer("🔑 Kino üçin kod ýaz (meselem: 101):")


@router.message(AddMovie.code)
async def admin_add_code(message: Message, state: FSMContext):
    if db.get_movie_by_code(message.text.strip()):
        await message.answer("⚠️ Bu kod eýýäm bar. Başga kod ýaz:")
        return
    await state.update_data(code=message.text.strip())
    await state.set_state(AddMovie.title)
    await message.answer("🎬 Kinonyň adyny ýaz:")


@router.message(AddMovie.title)
async def admin_add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddMovie.year)
    await message.answer("📅 Ýylyny ýaz:")


@router.message(AddMovie.year)
async def admin_add_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text.strip())
    await state.set_state(AddMovie.country)
    await message.answer("🌍 Ýurdyny ýaz:")


@router.message(AddMovie.country)
async def admin_add_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    genre_list = ", ".join(GENRES.keys())
    await state.set_state(AddMovie.genre)
    await message.answer(f"🎭 Žanryny ýaz ({genre_list}):")


@router.message(AddMovie.genre)
async def admin_add_genre(message: Message, state: FSMContext):
    genre = message.text.strip().lower()
    if genre not in GENRES:
        await message.answer(f"⚠️ Nädogry žanr. Şulardan birini ýaz: {', '.join(GENRES.keys())}")
        return
    await state.update_data(genre=genre)
    await state.set_state(AddMovie.description)
    await message.answer("📝 Gysgaça mazmunyny ýaz:")


@router.message(AddMovie.description)
async def admin_add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddMovie.video)
    await message.answer("🎥 Indi kino faýlyny (wideo) iber:")


@router.message(AddMovie.video, F.video)
async def admin_add_video(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_movie(
        code=data["code"], title=data["title"], year=data["year"],
        country=data["country"], genre=data["genre"],
        description=data["description"], file_id=message.video.file_id,
    )
    await state.clear()
    await message.answer(f"✅ Kino goşuldy! Kod: {data['code']}")


@router.message(AddMovie.video)
async def admin_add_video_wrong(message: Message):
    await message.answer("⚠️ Wideo faýl iberiň.")


@router.message(Command("delmovie"))
async def admin_del_movie(message: Message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Ulanyş: /delmovie <kod>")
        return
    if db.delete_movie(parts[1].strip()):
        await message.answer("🗑 Öçürildi.")
    else:
        await message.answer("❌ Bu kod tapylmady.")


@router.message(Command("addchannel"))
async def admin_add_channel(message: Message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer(
            "Ulanyş: /addchannel <chat_id> <at> <invite_link>\n"
            "Meselem: /addchannel -1001234567890 KanalAdy https://t.me/kanal"
        )
        return
    _, chat_id, title, link = parts
    db.add_channel(chat_id, title, link)
    await message.answer("✅ Kanal goşuldy.")


@router.message(Command("delchannel"))
async def admin_del_channel(message: Message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Ulanyş: /delchannel <chat_id>")
        return
    if db.remove_channel(parts[1].strip()):
        await message.answer("🗑 Kanal öçürildi.")
    else:
        await message.answer("❌ Tapylmady.")


@router.message(Command("cancel"))
async def admin_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Ýatyryldy.")


async def main():
    db.init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
