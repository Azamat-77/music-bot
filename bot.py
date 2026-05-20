import os
import asyncio
import sqlite3
import yt_dlp

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ================= SETTINGS =================

ADMIN_ID = 7562363422

BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"
API_ID = 38920950
API_HASH = "1b2b3131134f901228acd5fa464c5eb5"

START_PHOTO = "https://i.ibb.co/tpjt60kq/IMG-20260328-11432.jpg"

# ================= BOT =================

bot = Client(
    "music_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ================= FOLDERS =================

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ================= USERS =================

USER_FILE = "users.txt"
open(USER_FILE, "a").close()

# ================= DATABASE =================

db = sqlite3.connect(
    "music.db",
    check_same_thread=False
)

cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    query TEXT UNIQUE,
    file_id TEXT
)
""")

db.commit()

# ================= KEYBOARD =================

keyboard = ReplyKeyboardMarkup(
    [["🎵 Qo‘shiq qidirish"]],
    resize_keyboard=True
)

# ================= START =================

@bot.on_message(filters.command("start"))
async def start(client, message):

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    if str(message.from_user.id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{message.from_user.id}\n")

    admin_buttons = None

    if message.from_user.id == ADMIN_ID:

        admin_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "👥 Obunachilar",
                    callback_data="subs"
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Reklama",
                    callback_data="broadcast"
                )
            ]
        ])

    await message.reply_photo(
        photo=START_PHOTO,
        caption=(
            "🎵 MUSIC BOT\n\n"
            "🎶 Qo‘shiq nomini yuboring"
        ),
        reply_markup=keyboard if admin_buttons is None else admin_buttons
    )

# ================= SEARCH FUNCTION =================

def search_music(query):

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            f"ytsearch5:{query}",
            download=False
        )

        entries = info.get("entries", [])

        if not entries:
            return None, None

        bad_words = [
            "slowed",
            "remix",
            "bass boosted",
            "reverb",
            "short",
            "status"
        ]

        best = None

        for v in entries:

            title = v.get("title", "").lower()

            if any(b in title for b in bad_words):
                continue

            best = v
            break

        if not best:
            best = entries[0]

        info2 = ydl.extract_info(
            best["url"],
            download=True
        )

        path = ydl.prepare_filename(info2)

        base, _ = os.path.splitext(path)

        final_path = None

        for ext in [".mp3", ".m4a", ".webm", ".opus"]:
            if os.path.exists(base + ext):
                final_path = base + ext
                break

        if not final_path:
            final_path = path

        return best["title"], final_path

# ================= MUSIC SEARCH =================

@bot.on_message(filters.text & ~filters.command("start"))
async def music(client, message):

    text = message.text.strip()

    if text == "🎵 Qo‘shiq qidirish":
        await message.reply(
            "🎶 Qo‘shiq nomini yuboring"
        )
        return

    query = text.lower()

    await client.send_chat_action(
        message.chat.id,
        ChatAction.UPLOAD_AUDIO
    )

    loading = await message.reply(
        "⏳ Qidirilmoqda..."
    )

    # ===== CACHE =====

    cur.execute(
        "SELECT file_id FROM songs WHERE query=?",
        (query,)
    )

    data = cur.fetchone()

    if data:

        await message.reply_audio(data[0])

        await loading.delete()

        return

    # ===== DOWNLOAD =====

    try:

        title, file_path = await asyncio.to_thread(
            search_music,
            query
        )

        if not file_path:

            await loading.edit(
                "❌ Topilmadi"
            )

            return

        sent = await message.reply_audio(
            audio=file_path,
            caption=f"🎵 {title}"
        )

        try:

            cur.execute(
                "INSERT OR REPLACE INTO songs VALUES (?, ?)",
                (
                    query,
                    sent.audio.file_id
                )
            )

            db.commit()

        except:
            pass

        await loading.delete()

    except Exception as e:

        print(e)

        await loading.edit(
            "❌ Xatolik yuz berdi"
        )

# ================= ADMIN =================

@bot.on_callback_query(filters.regex("subs"))
async def subs(client, callback_query):

    if callback_query.from_user.id != ADMIN_ID:
        return

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    await callback_query.answer(
        f"👥 Obunachilar: {len(users)}",
        show_alert=True
    )

@bot.on_callback_query(filters.regex("broadcast"))
async def broadcast(client, callback_query):

    if callback_query.from_user.id != ADMIN_ID:
        return

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    for user in users:

        try:
            await client.send_message(
                int(user),
                "📢 Admin xabari!"
            )
        except:
            pass

    await callback_query.answer(
        "✅ Yuborildi",
        show_alert=True
    )

# ================= RUN =================

print("Bot ishga tushdi...")

bot.run()
