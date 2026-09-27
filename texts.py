# Foydalanuvchiga chiqadigan barcha matnlar (Turk / Rus tillarida)

GENRES = {
    "horror":  {"tr": "😱 Korku",        "ru": "😱 Ужасы"},
    "love":    {"tr": "❤️ Romantik",     "ru": "❤️ Мелодрама"},
    "comedy":  {"tr": "😂 Komedi",       "ru": "😂 Комедия"},
    "action":  {"tr": "💥 Aksiyon",      "ru": "💥 Боевик"},
    "drama":   {"tr": "🎭 Drama",        "ru": "🎭 Драма"},
    "fantasy": {"tr": "🚀 Fantastik",    "ru": "🚀 Фантастика"},
    "crime":   {"tr": "🔫 Suç",          "ru": "🔫 Криминал"},
    "cartoon": {"tr": "🧸 Çizgi film",   "ru": "🧸 Мультфильм"},
}


def genre_label(genre_key: str, lang: str) -> str:
    g = GENRES.get(genre_key)
    if not g:
        return genre_key
    return g.get(lang, g.get("tr"))


TEXTS = {
    "tr": {
        "lang_name": "🇹🇷 Türkçe",
        "choose_lang": "🌐 Lütfen dilinizi seçin / Iltimos, tilni tanlang:",
        "lang_saved_prefix": "✅ Dil: Türkçe\n\n",
        "welcome": (
            "Merhaba, {name}! 👋\n\n"
            "🎬 <b>Filmlar</b> botuna hoş geldin!\n\n"
            "🔑 Film kodunu yazarak arayabilirsin\n"
            "🎭 Ya da aşağıdan bir tür seçebilirsin\n"
            "🔍 Herhangi bir sohbette <code>@{bot_username}</code> yazıp film adı ile de arayabilirsin"
        ),
        "subscribe_required": "❗️ Botu kullanabilmek için önce aşağıdaki kanala abone olmalısın:",
        "subscribe_channel_btn": "📢 {title}",
        "check_sub_btn": "✅ Kontrol et",
        "not_subscribed_alert": "❌ Henüz kanala abone olmadın!",
        "back_after_sub": "✅ Teşekkürler! Şimdi film kodu yaz ya da aşağıdan tür seç:",
        "choose_genre": "🎭 Bir tür seç:",
        "genre_movies_header": "{genre} türündeki filmler:\n\n",
        "genre_movie_line": "🔑 <code>{code}</code> — {title} ({year})\n",
        "no_movies_in_genre": "😔 Bu türde henüz film yok.",
        "prev_btn": "⬅️ Geri",
        "next_btn": "İleri ➡️",
        "back_genres_btn": "🔙 Türler",
        "movie_not_found": "❌ Bu koda ait film bulunamadı.",
        "search_results_header": "🔍 Bulunan filmler:\n\n",
        "search_nothing": "❌ Hiçbir şey bulunamadı. Kodu ya da film adını doğru yazdığından emin ol.",
        "movie_caption": (
            "🎬 <b>{title}</b>\n"
            "📅 Yıl: {year}\n"
            "🌍 Ülke: {country}\n"
            "🎭 Tür: {genre}\n\n"
            "📝 {description}\n\n"
            "🔑 Kod: <code>{code}</code>"
        ),
        "watch_btn": "🎬 Filmi izle",
        "not_admin": "⛔️ Bu komut sadece admin içindir.",
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "choose_lang": "🌐 Iltimos, tilni tanlang / Пожалуйста, выберите язык:",
        "lang_saved_prefix": "✅ Язык: Русский\n\n",
        "welcome": (
            "Привет, {name}! 👋\n\n"
            "🎬 Добро пожаловать в бот <b>Filmlar</b>!\n\n"
            "🔑 Отправь код фильма для поиска\n"
            "🎭 Или выбери жанр ниже\n"
            "🔍 В любом чате можно найти фильм, набрав <code>@{bot_username}</code> и название"
        ),
        "subscribe_required": "❗️ Чтобы пользоваться ботом, сначала подпишись на канал:",
        "subscribe_channel_btn": "📢 {title}",
        "check_sub_btn": "✅ Проверить",
        "not_subscribed_alert": "❌ Ты ещё не подписан на канал!",
        "back_after_sub": "✅ Спасибо! Теперь отправь код фильма или выбери жанр:",
        "choose_genre": "🎭 Выбери жанр:",
        "genre_movies_header": "Фильмы в жанре {genre}:\n\n",
        "genre_movie_line": "🔑 <code>{code}</code> — {title} ({year})\n",
        "no_movies_in_genre": "😔 В этом жанре пока нет фильмов.",
        "prev_btn": "⬅️ Назад",
        "next_btn": "Вперёд ➡️",
        "back_genres_btn": "🔙 Жанры",
        "movie_not_found": "❌ Фильм с таким кодом не найден.",
        "search_results_header": "🔍 Найденные фильмы:\n\n",
        "search_nothing": "❌ Ничего не найдено. Проверь код или название фильма.",
        "movie_caption": (
            "🎬 <b>{title}</b>\n"
            "📅 Год: {year}\n"
            "🌍 Страна: {country}\n"
            "🎭 Жанр: {genre}\n\n"
            "📝 {description}\n\n"
            "🔑 Код: <code>{code}</code>"
        ),
        "watch_btn": "🎬 Смотреть фильм",
        "not_admin": "⛔️ Эта команда только для админа.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TEXTS else "tr"
    template = TEXTS[lang].get(key, TEXTS["tr"].get(key, key))
    return template.format(**kwargs) if kwargs else template
