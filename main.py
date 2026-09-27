import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineQuery, FSInputFile,
    InlineQueryResultArticle, InputTextMessageContent,
)

from config import BOT_TOKEN, ADMIN_IDS, LOGO_PATH
import db
from texts import t, genre_label, GENRES
from keyboards import (
    language_keyboard, genres_keyboard, subscribe_keyboard,
    genre_pagination_keyboard, movie_deep_link_keyboard,
    admin_panel_keyboard, admin_genre_choice_keyboard,
    admin_cancel_keyboard, channels_manage_keyboard,
)

logging.basicConfig(level=logging.INFO)

router = Router()

# user_id -> deep-link kod (obuna bo'lmagan holatda saqlanadi, obunadan so'ng ishlatiladi)
pending_start: dict[int, str] = {}


class AddMovie(StatesGroup):
    code = State()
    title = State()
    year = State()
    country = State()
    genre = State()
    description = State()
    video = State()


class DeleteMovie(StatesGroup):
    code = State()


# ---------- HELPERS ----------

def _parse_chat_id(chat_id_str: str):
    try:
        return int(chat_id_str)
    except (TypeError, ValueError):
        return chat_id_str


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    channels = db.get_channels()
    if not channels:
        return True
    for ch in channels:
        try:
            member = await bot.get_chat_member(_parse_chat_id(ch["chat_id"]), user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            # Bot kanalda admin bo'lmasa yoki username noto'g'ri bo'lsa - tekshira olmaymiz,
            # bunday holatda foydalanuvchini bloklamaymiz.
            continue
    return True


def user_lang(user_id: int) -> str:
    return db.get_user_lang(user_id)


def movie_caption(movie, lang: str) -> str:
    return t(
        lang, "movie_caption",
        title=movie["title"], year=movie["year"], country=movie["country"],
        genre=genre_label(movie["genre"], lang), description=movie["description"],
        code=movie["code"],
    )


async def _send_movie_file(bot: Bot, chat_id: int, movie, caption: str):
    content_type = movie["content_type"] or "video"
    if content_type == "document":
        await bot.send_document(chat_id, movie["file_id"], caption=caption, parse_mode="HTML")
    elif content_type == "animation":
        await bot.send_animation(chat_id, movie["file_id"], caption=caption, parse_mode="HTML")
    else:
        await bot.send_video(chat_id, movie["file_id"], caption=caption, parse_mode="HTML")


async def send_movie(bot: Bot, chat_id: int, code: str, lang: str):
    movie = db.get_movie_by_code(code)
    if not movie:
        await bot.send_message(chat_id, t(lang, "movie_not_found"))
        return
    await _send_movie_file(bot, chat_id, movie, movie_caption(movie, lang))


async def show_main_menu(bot: Bot, chat_id: int, user, lang: str):
    me = await bot.get_me()
    caption = t(lang, "welcome", name=user.first_name or "", bot_username=me.username)
    try:
        await bot.send_photo(
            chat_id, FSInputFile(LOGO_PATH),
            caption=caption, parse_mode="HTML",
            reply_markup=genres_keyboard(lang),
        )
    except Exception:
        await bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=genres_keyboard(lang))


async def proceed_after_lang(bot: Bot, chat_id: int, user, lang: str):
    """Til tanlangandan (yoki allaqachon tanlangan bo'lsa start bosilgandan) keyingi qadam."""
    if not await is_subscribed(bot, user.id):
        channels = db.get_channels()
        await bot.send_message(
            chat_id, t(lang, "subscribe_required"),
            reply_markup=subscribe_keyboard(channels, lang),
        )
        return
    code = pending_start.pop(user.id, None)
    await show_main_menu(bot, chat_id, user, lang)
    if code:
        await send_movie(bot, chat_id, code, lang)


# ---------- USER: START / LANGUAGE ----------

@router.message(CommandStart())
async def cmd_start(message: Message, command, bot: Bot):
    if command.args:
        pending_start[message.from_user.id] = command.args
    await message.answer(
        t("tr", "choose_lang"),
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def cb_set_lang(callback: CallbackQuery, bot: Bot):
    lang = callback.data.split(":")[1]
    db.set_user(callback.from_user.id, lang, callback.from_user.first_name)
    await callback.message.delete()
    await proceed_after_lang(bot, callback.message.chat.id, callback.from_user, lang)
    await callback.answer()


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: CallbackQuery, bot: Bot):
    lang = user_lang(callback.from_user.id)
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.delete()
        code = pending_start.pop(callback.from_user.id, None)
        await show_main_menu(bot, callback.message.chat.id, callback.from_user, lang)
        if code:
            await send_movie(bot, callback.message.chat.id, code, lang)
    else:
        await callback.answer(t(lang, "not_subscribed_alert"), show_alert=True)


@router.callback_query(F.data == "back_genres")
async def cb_back_genres(callback: CallbackQuery):
    lang = user_lang(callback.from_user.id)
    try:
        await callback.message.edit_caption(caption=t(lang, "choose_genre"), reply_markup=genres_keyboard(lang))
    except Exception:
        try:
            await callback.message.edit_text(t(lang, "choose_genre"), reply_markup=genres_keyboard(lang))
        except Exception:
            await callback.message.answer(t(lang, "choose_genre"), reply_markup=genres_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("genre:"))
async def cb_genre(callback: CallbackQuery, bot: Bot):
    lang = user_lang(callback.from_user.id)
    if not await is_subscribed(bot, callback.from_user.id):
        await callback.answer(t(lang, "not_subscribed_alert"), show_alert=True)
        return
    _, genre, offset = callback.data.split(":")
    offset = int(offset)
    movies = db.get_movies_by_genre(genre, limit=10, offset=offset)
    total = db.count_movies_by_genre(genre)
    if not movies:
        await callback.answer(t(lang, "no_movies_in_genre"), show_alert=True)
        return
    text = t(lang, "genre_movies_header", genre=genre_label(genre, lang))
    text += "".join(
        t(lang, "genre_movie_line", code=m["code"], title=m["title"], year=m["year"]) for m in movies
    )
    has_more = offset + 10 < total
    markup = genre_pagination_keyboard(genre, offset, has_more, lang)
    try:
        await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=markup)
    await callback.answer()


@router.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def msg_code_search(message: Message, bot: Bot):
    lang = user_lang(message.from_user.id)
    if not await is_subscribed(bot, message.from_user.id):
        channels = db.get_channels()
        await message.answer(t(lang, "subscribe_required"), reply_markup=subscribe_keyboard(channels, lang))
        return
    code = message.text.strip()
    movie = db.get_movie_by_code(code)
    if movie:
        await _send_movie_file(bot, message.chat.id, movie, movie_caption(movie, lang))
        return
    results = db.search_movies_by_title(code)
    if results:
        text = t(lang, "search_results_header") + "".join(
            t(lang, "genre_movie_line", code=m["code"], title=m["title"], year=m["year"]) for m in results
        )
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(t(lang, "search_nothing"))


@router.inline_query()
async def inline_search(inline_query: InlineQuery, bot: Bot):
    query = inline_query.query.strip()
    if not query:
        await inline_query.answer([], cache_time=1)
        return
    lang = user_lang(inline_query.from_user.id)
    movies = db.search_movies_by_title(query)
    me = await bot.get_me()
    results = []
    for m in movies[:15]:
        results.append(
            InlineQueryResultArticle(
                id=m["code"],
                title=f"{m['title']} ({m['year']})",
                description=f"{genre_label(m['genre'], lang)} | {m['country']}",
                input_message_content=InputTextMessageContent(
                    message_text=movie_caption(m, lang), parse_mode="HTML"
                ),
                reply_markup=movie_deep_link_keyboard(me.username, m["code"], lang),
            )
        )
    await inline_query.answer(results, cache_time=1, is_personal=True)


# ---------- ADMIN ----------

def admin_only(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not admin_only(message.from_user.id):
        return
    await message.answer("🛠 Admin panel:", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "adm:back")
async def adm_back(callback: CallbackQuery):
    if not admin_only(callback.from_user.id):
        return
    await callback.message.edit_text("🛠 Admin panel:", reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "adm:cancel")
async def adm_cancel(callback: CallbackQuery, state: FSMContext):
    if not admin_only(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.", reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def adm_stats(callback: CallbackQuery):
    if not admin_only(callback.from_user.id):
        return
    text = (
        f"📊 Statistika:\n\n"
        f"🎬 Kinolar soni: {db.count_movies()}\n"
        f"👤 Foydalanuvchilar soni: {db.count_users()}"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "adm:channels")
async def adm_channels(callback: CallbackQuery):
    if not admin_only(callback.from_user.id):
        return
    channels = db.get_channels()
    text = "📋 Majburiy obuna kanallari:\n\n" + (
        "\n".join(f"• {ch['title'] or ch['chat_id']} — {ch['chat_id']}" for ch in channels)
        or "Hech qanday kanal yo'q."
    )
    text += (
        "\n\nYangi kanal qo'shish uchun:\n"
        "<code>/addchannel &lt;chat_id&gt; &lt;nomi&gt; &lt;link&gt;</code>\n"
        "Masalan: <code>/addchannel @FiImIar Filmlar https://t.me/FiImIar</code>"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=channels_manage_keyboard(channels),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admchdel:"))
async def adm_channel_delete(callback: CallbackQuery):
    if not admin_only(callback.from_user.id):
        return
    chat_id = callback.data.split(":", 1)[1]
    db.remove_channel(chat_id)
    await callback.answer("🗑 O'chirildi.")
    channels = db.get_channels()
    text = "📋 Majburiy obuna kanallari:\n\n" + (
        "\n".join(f"• {ch['title'] or ch['chat_id']} — {ch['chat_id']}" for ch in channels)
        or "Hech qanday kanal yo'q."
    )
    await callback.message.edit_text(text, reply_markup=channels_manage_keyboard(channels))


# --- Kino qo'shish (tugma orqali ham, /addmovie yoki /admovie orqali ham) ---

@router.callback_query(F.data == "adm:add")
async def adm_add_start(callback: CallbackQuery, state: FSMContext):
    if not admin_only(callback.from_user.id):
        return
    await state.set_state(AddMovie.code)
    await callback.message.edit_text(
        "🔑 Kino uchun kod yozing (masalan: 101):", reply_markup=admin_cancel_keyboard(),
    )
    await callback.answer()


@router.message(Command("addmovie", "admovie"))
async def admin_add_start_cmd(message: Message, state: FSMContext):
    if not admin_only(message.from_user.id):
        await message.answer(t(user_lang(message.from_user.id), "not_admin"))
        return
    await state.set_state(AddMovie.code)
    await message.answer("🔑 Kino uchun kod yozing (masalan: 101):", reply_markup=admin_cancel_keyboard())


@router.message(AddMovie.code)
async def admin_add_code(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, matn (kod) yozing:")
        return
    code = message.text.strip()
    if db.get_movie_by_code(code):
        await message.answer("⚠️ Bu kod band. Boshqa kod yozing:")
        return
    await state.update_data(code=code)
    await state.set_state(AddMovie.title)
    await message.answer("🎬 Kino nomini yozing:")


@router.message(AddMovie.title)
async def admin_add_title(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, matn (nom) yozing:")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddMovie.year)
    await message.answer("📅 Yilini yozing:")


@router.message(AddMovie.year)
async def admin_add_year(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, matn (yil) yozing:")
        return
    await state.update_data(year=message.text.strip())
    await state.set_state(AddMovie.country)
    await message.answer("🌍 Davlatini yozing:")


@router.message(AddMovie.country)
async def admin_add_country(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, matn (davlat) yozing:")
        return
    await state.update_data(country=message.text.strip())
    await state.set_state(AddMovie.genre)
    await message.answer("🎭 Janrini tanlang:", reply_markup=admin_genre_choice_keyboard())


@router.callback_query(AddMovie.genre, F.data.startswith("admgenre:"))
async def admin_add_genre(callback: CallbackQuery, state: FSMContext):
    genre = callback.data.split(":", 1)[1]
    if genre not in GENRES:
        await callback.answer("⚠️ Noto'g'ri janr.", show_alert=True)
        return
    await state.update_data(genre=genre)
    await state.set_state(AddMovie.description)
    await callback.message.edit_text("📝 Qisqacha tavsif yozing:")
    await callback.answer()


@router.message(AddMovie.description)
async def admin_add_description(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, matn (tavsif) yozing:")
        return
    await state.update_data(description=message.text.strip())
    await state.set_state(AddMovie.video)
    await message.answer(
        "🎥 Endi kino faylini yuboring (video/hujjat) yoki kanaldan forward qiling:",
        reply_markup=admin_cancel_keyboard(),
    )


@router.message(AddMovie.video, F.video | F.document | F.animation)
async def admin_add_video(message: Message, state: FSMContext):
    if message.video:
        file_id, content_type = message.video.file_id, "video"
    elif message.animation:
        file_id, content_type = message.animation.file_id, "animation"
    else:
        doc = message.document
        mime = (doc.mime_type or "")
        if not (mime.startswith("video/") or (doc.file_name or "").lower().endswith((".mp4", ".mkv", ".avi", ".mov"))):
            await message.answer("⚠️ Bu fayl video ko'rinishida emas. Video yoki film faylini yuboring.")
            return
        file_id, content_type = doc.file_id, "document"

    data = await state.get_data()
    db.add_movie(
        code=data["code"], title=data["title"], year=data["year"],
        country=data["country"], genre=data["genre"],
        description=data["description"], file_id=file_id, content_type=content_type,
    )
    await state.clear()
    await message.answer(f"✅ Kino qo'shildi! Kod: {data['code']}", reply_markup=admin_panel_keyboard())


@router.message(AddMovie.video)
async def admin_add_video_wrong(message: Message):
    await message.answer("⚠️ Iltimos video, hujjat (film fayli) yuboring yoki forward qiling.")


# --- Kino o'chirish ---

@router.callback_query(F.data == "adm:del")
async def adm_del_start(callback: CallbackQuery, state: FSMContext):
    if not admin_only(callback.from_user.id):
        return
    await state.set_state(DeleteMovie.code)
    await callback.message.edit_text("🗑 O'chiriladigan kino kodini yozing:", reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(Command("delmovie"))
async def admin_del_movie_cmd(message: Message):
    if not admin_only(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /delmovie <kod>")
        return
    if db.delete_movie(parts[1].strip()):
        await message.answer("🗑 O'chirildi.")
    else:
        await message.answer("❌ Bu kod topilmadi.")


@router.message(DeleteMovie.code)
async def admin_del_movie_state(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("⚠️ Iltimos, kino kodini matn sifatida yozing:")
        return
    code = message.text.strip()
    await state.clear()
    if db.delete_movie(code):
        await message.answer(f"🗑 {code} o'chirildi.", reply_markup=admin_panel_keyboard())
    else:
        await message.answer("❌ Bu kod topilmadi.", reply_markup=admin_panel_keyboard())


# --- Kanal qo'shish/o'chirish (buyruq orqali) ---

@router.message(Command("addchannel"))
async def admin_add_channel(message: Message):
    if not admin_only(message.from_user.id):
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer(
            "Usage: /addchannel <chat_id> <nomi> <link>\n"
            "Masalan: /addchannel @FiImIar Filmlar https://t.me/FiImIar"
        )
        return
    _, chat_id, title, link = parts
    db.add_channel(chat_id, title, link)
    await message.answer("✅ Kanal qo'shildi.")


@router.message(Command("delchannel"))
async def admin_del_channel(message: Message):
    if not admin_only(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /delchannel <chat_id>")
        return
    if db.remove_channel(parts[1].strip()):
        await message.answer("🗑 Kanal o'chirildi.")
    else:
        await message.answer("❌ Topilmadi.")


@router.message(Command("cancel"))
async def admin_cancel_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.")


async def main():
    db.init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
