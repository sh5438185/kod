import os

# Kino botynyň tokenini @BotFather-dan al we şu ýere ýaz
# (ýa-da BOT_TOKEN atly environment variable hökmünde ber)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8943368291:AAHLKglzQ8Ky9IN4KyjkSVkAOrs8e2wRkQQ")

# Admin bolup bilýän ulanyjylaryň Telegram ID-leri (vergul bilen aýryp bilersiň)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "719797288").split(",") if x.strip()]

DB_PATH = "movies.db"
