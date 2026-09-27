# Filmlar Bot

Telegram kino-kod boti. Foydalanuvchi tilni tanlaydi (Turk / Rus), so'ng logotip va
salomlashuv chiqadi, kino kodi yoki janr orqali qidiradi. Majburiy obuna va to'liq
ishlaydigan admin panel bilan.

## O'rnatish

```bash
pip install -r requirements.txt
python main.py
```

Token va admin ID'larni environment variable orqali (tavsiya etiladi) yoki
`config.py` ichida to'g'ridan-to'g'ri o'zgartirish mumkin:

```bash
export BOT_TOKEN="123456:ABC..."
export ADMIN_IDS="7197972883"
export CHANNEL_USERNAME="@FiImIar"
export CHANNEL_URL="https://t.me/FiImIar"
```

`logo.png` fayli papkada bo'lishi shart — bu til tanlangandan keyin chiqadigan rasm.

## Foydalanuvchi oqimi

1. `/start` — til tanlash (🇹🇷 Türkçe / 🇷🇺 Русский) so'raladi.
2. Til tanlangach — agar kanalga (@FiImIar) obuna bo'lmagan bo'lsa, obuna bo'lish
   so'raladi ("✅ Kontrol et / Проверить" tugmasi bilan).
3. Obuna tasdiqlangach — logotip + shaxsiy salomlashuv (ismi bilan) + janrlar
   ro'yxati chiqadi.
4. Foydalanuvchi kino kodini yuborishi yoki janr tanlashi mumkin.
5. Har qanday chatda `@bot_username kino_nomi` deb yozib inline qidiruv ham ishlaydi.
6. Deep-link orqali ham ishlaydi: `t.me/bot?start=101` — agar obuna bo'lmasa, avval
   obunani so'raydi, obunadan so'ng o'sha kino avtomatik yuboriladi.

## Admin panel

Admin (ID: `7197972883`, `config.py`/`ADMIN_IDS` orqali boshqariladi) uchun:

- `/admin` — tugmali admin panel: kino qo'shish, kino o'chirish, statistika, kanallar.
- `/addmovie` yoki `/admovie` — ikkalasi ham ishlaydi, kino qo'shish jarayonini
  boshlaydi (avvalgi botda faqat bittasi ishlar edi va u ham xato berayotgan edi —
  endi ikkalasi ham to'g'ridan-to'g'ri va admin panel tugmasi orqali ham ishlaydi).
- Kino qo'shishda: kod → nom → yil → davlat → janr (tugmalardan tanlanadi) →
  tavsif → **fayl**. Fayl bosqichida video, hujjat (document) ko'rinishidagi kino
  fayli yoki **forward qilingan** xabar ham qabul qilinadi — barchasidan `file_id`
  to'g'ri olinadi va saqlanadi.
- `/delmovie <kod>` yoki admin paneldagi "🗑 Kino o'chirish" tugmasi.
- `/addchannel <chat_id> <nomi> <link>` va `/delchannel <chat_id>` — majburiy
  obuna kanallarini boshqarish (bir nechta kanal qo'shish ham mumkin).
- `/cancel` — istalgan bosqichda jarayonni bekor qiladi.

## Nima o'zgardi (eski koddan)

- Bot matnlari to'liq Turk va Rus tiliga o'girildi, `/start`da til tanlash
  qo'shildi va tanlangan til `users` jadvalida saqlanadi.
- Til tanlangandan keyin logotip (`logo.png`) va foydalanuvchi ismi bilan
  shaxsiylashtirilgan salomlashuv qo'shildi.
- `/addmovie` ishlamayotgan muammo hal qilindi: endi `/addmovie` va `/admovie`
  ikkalasi ham ishlaydi, ustiga admin panelda tugma orqali ham boshlash mumkin —
  buyruqni eslab yurish shart emas.
- Kino faylini faqat "video" sifatida emas, forward qilingan yoki hujjat
  (document) sifatida yuborilgan fayllardan ham to'g'ri `file_id` olinadigan
  bo'ldi (avvalgi versiya faqat `message.video` kutar edi va boshqa turdagi
  fayllarni rad etar edi).
- To'liq ishlaydigan admin panel (`/admin`) qo'shildi: statistika (kinolar va
  foydalanuvchilar soni), kanallarni ko'rish/o'chirish, kino qo'shish/o'chirish —
  barchasi tugmalar orqali.
- Majburiy obuna standart holatda `https://t.me/FiImIar` kanaliga sozlangan,
  kerak bo'lsa admin panel/buyruqlar orqali boshqa kanallar ham qo'shiladi.
