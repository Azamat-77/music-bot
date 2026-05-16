import asyncio
import os
import yt_dlp
import asyncio
import sqlite3
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# 🔧 BOT SOZLAMALARI
ADMIN_ID = 7562363422
BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"

bot = Client(
    "music_bot",
    bot_token=BOT_TOKEN,
    api_id=38920950,
    api_hash="YOUR_API_HASH",
    sleep_threshold=60
)

# 📁 PAPKA
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 📌 KEYBOARD
keyboard = ReplyKeyboardMarkup(
    [["Qo‘shiq nomini yoz"]],
    resize_keyboard=True
)

# 📂 USERS FILE
USER_FILE = "users.txt"
if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()

# 🔥 DATABASE
db = sqlite3.connect("music.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    name TEXT UNIQUE,
    file_id TEXT,
    path TEXT
)
""")
db.commit()

# 🚀 START
@bot.on_message(filters.command("start"))
async def start(client, message):
    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    if str(message.from_user.id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{message.from_user.id}\n")

    await message.reply_photo(
        photo="https://i.ibb.co/tpjt60kq/IMG-20260328-11432.jpg",
        caption="🎵 Salom! Qo‘shiq nomini yoz 🎵",
        reply_markup=keyboard
    )

# 🔥 QO‘SHIQ QIDIRISH
@bot.on_message(filters.text & ~filters.regex("^/"))
async def find_song(client, message):

    if message.text == "Qo‘shiq nomini yoz":
        await message.reply("🎶 Qo‘shiq nomini yozing...")
        return

    loading = await message.reply_text("⏳ Qidirilyapti...")

    query = message.text.lower().strip()

    # CACHE
    cur.execute("SELECT file_id, path FROM songs WHERE name=?", (query,))
    data = cur.fetchone()

    if data:
        file_id, path = data
        try:
            await message.reply_audio(file_id)
            await loading.delete()
            return
        except:
            pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)

            if not info.get("entries"):
                await loading.edit("❌ Topilmadi!")
                return

            video = info['entries'][0]
            file_path = ydl.prepare_filename(video)

        await loading.edit("🎧 Yuklanmoqda...")

        sent = await message.reply_audio(file_path, caption=video['title'])

        # 🔥 CACHE SAVE (TO‘G‘RILANGAN)
        try:
            file_id = sent.audio.file_id

            cur.execute(
                "INSERT OR REPLACE INTO songs (name, file_id, path) VALUES (?, ?, ?)",
                (query, file_id, file_path)
            )
            db.commit()

        except Exception as e:
            print("DB error:", e)

        await loading.delete()

    except Exception as e:
        print(e)
        await loading.edit("❌ Xatolik yuz berdi!")

# ▶️ RUN
async def main():
    print("🚀 Bot ishga tushdi...")

    await bot.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
