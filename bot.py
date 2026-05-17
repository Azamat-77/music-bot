import os
import yt_dlp
import asyncio
import sqlite3
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# 🔧 BOT SOZLAMALARI
ADMIN_ID = 7562363422

BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"

API_ID = 38920950
API_HASH = "1b2b3131134f901228acd5fa464c5eb5"

bot = Client(
    "music_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    sleep_threshold=60
)

# 📁 PAPKA
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 📂 USERS FILE
USER_FILE = "users.txt"

if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()

# 🔥 DATABASE
db = sqlite3.connect(
    "music.db",
    check_same_thread=False
)

cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    name TEXT UNIQUE,
    file_id TEXT,
    path TEXT
)
""")

db.commit()

# 📌 KEYBOARD
keyboard = ReplyKeyboardMarkup(
    [["Qo‘shiq nomini yoz"]],
    resize_keyboard=True
)

# 🚀 START
@bot.on_message(filters.command("start"))
async def start(client, message):

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    if str(message.from_user.id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{message.from_user.id}\n")

    if message.from_user.id == ADMIN_ID:

        admin_buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👁 Obunachilarni ko‘rish",
                        callback_data="check_subs"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📢 Obunachilarga xabar",
                        callback_data="broadcast"
                    )
                ]
            ]
        )

    else:
        admin_buttons = None

    await message.reply_photo(
        photo="https://i.ibb.co/tpjt60kq/IMG-20260328-11432.jpg",
        caption="🎵 Salom! Qo‘shiq nomini yozing 🎵",
        reply_markup=keyboard if admin_buttons is None else admin_buttons
    )

# 🎵 QO‘SHIQ QIDIRISH
@bot.on_message(filters.text & ~filters.regex("^/"))
async def find_song(client, message):

    if message.text == "Qo‘shiq nomini yoz":
        await message.reply("🎶 Qo‘shiq nomini yozing...")
        return

    query = message.text.lower().strip()

    await client.send_chat_action(
        message.chat.id,
        ChatAction.TYPING
    )

    loading = await message.reply_text(
        "⏳ Qidirilyapti..."
    )

    # ⚡ CACHE TEKSHIRISH
    cur.execute(
        "SELECT file_id FROM songs WHERE name=?",
        (query,)
    )

    data = cur.fetchone()

    if data:

        file_id = data[0]

        try:
            await message.reply_audio(file_id)
            await loading.delete()
            return

        except:
            pass

    # 🔄 ANIMATION
    async def animate():

        while True:

            try:
                await loading.edit("⏳ Qidirilyapti...")
                await asyncio.sleep(1)

                await loading.edit("🔎 Kuting...")
                await asyncio.sleep(1)

                await loading.edit("🎧 Yuklanmoqda...")
                await asyncio.sleep(1)

            except:
                break

    task = asyncio.create_task(animate())

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True
    }

    try:

        # 🔥 THREADDA YUKLASH
        def download_song():

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(
                    f"ytsearch1:{query}",
                    download=True
                )

                if not info.get("entries"):
                    return None, None

                video = info["entries"][0]

                file_path = ydl.prepare_filename(video)

                return video, file_path

        video, file_path = await asyncio.to_thread(
            download_song
        )

        if not video:
            task.cancel()

            await loading.edit(
                "❌ Qo‘shiq topilmadi!"
            )

            return

        task.cancel()

        await loading.edit(
            "🎧 Yuklandi, yuborilmoqda..."
        )

        # 🎵 AUDIO YUBORISH
        sent = await message.reply_audio(
            audio=file_path,
            caption=video["title"]
        )

        # 💾 CACHE SAQLASH
        try:

            file_id = sent.audio.file_id

            cur.execute(
                "INSERT OR REPLACE INTO songs (name, file_id, path) VALUES (?, ?, ?)",
                (query, file_id, file_path)
            )

            db.commit()

        except:
            pass

        await loading.delete()

    except Exception as e:

<<<<<<< HEAD
# START BOT (FIXED - NO ASYNC)
if __name__ == "__main__":
    print("Bot started")
    bot.run()
=======
        task.cancel()

        print(e)

        await loading.edit(
            "❌ Xatolik yuz berdi!"
        )

# 👁 ADMIN PANEL
@bot.on_callback_query(filters.regex("check_subs"))
async def check_subs(client, callback_query):

    if callback_query.from_user.id != ADMIN_ID:

        await callback_query.answer(
            "❌ Bu knopka sizga emas!",
            show_alert=True
        )

        return

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    await callback_query.answer(
        f"👥 Obunachilar: {len(users)}",
        show_alert=True
    )

# 📢 BROADCAST
@bot.on_callback_query(filters.regex("broadcast"))
async def broadcast(client, callback_query):

    if callback_query.from_user.id != ADMIN_ID:

        await callback_query.answer(
            "❌ Bu knopka sizga emas!",
            show_alert=True
        )

        return

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    for user_id in users:

        try:
            await client.send_message(
                int(user_id),
                "📢 Admin xabari!"
            )

        except:
            pass

    await callback_query.answer(
        "✅ Yuborildi",
        show_alert=True
    )

# ▶️ RUN
print("✅ Bot ishga tushdi...")

bot.run()
>>>>>>> dc2c328 (update bot)
