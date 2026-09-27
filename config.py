import os

# Bot tokeni (@BotFather'dan) - environment variable BOT_TOKEN bilan ham berish mumkin
BOT_TOKEN = os.getenv("BOT_TOKEN", "8943368291:AAHLKglzQ8Ky9IN4KyjkSVkAOrs8e2wRkQQ")

# Admin bo'la oladigan Telegram ID'lar (vergul bilan ajratib bir nechta berish mumkin)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7197972883").split(",") if x.strip()]

# Majburiy obuna kanali
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@FiImIar")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/FiImIar")

DB_PATH = os.getenv("DB_PATH", "movies.db")

# Bot ishga tushganda yuboriladigan logotip
LOGO_PATH = os.getenv("LOGO_PATH", "logo.png")

DEFAULT_LANG = "tr"
SUPPORTED_LANGS = ("tr", "ru")
