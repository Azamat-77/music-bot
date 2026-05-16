import os
import sqlite3
import yt_dlp
import asyncio

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup
from pyrogram.idle import idle

# 🔧 SETTINGS
API_ID = 38920950
API_HASH = "1b2b3131134f901228acd5fa464c5eb5"
BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"

bot = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 📁 FOLDER
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🎛 BUTTON
keyboard = ReplyKeyboardMarkup(
    [["Qo‘shiq nomini yoz"]],
    resize_keyboard=True
)

# 📦 DATABASE
db = sqlite3.connect("music.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    name TEXT UNIQUE,
    file_id TEXT
)
""")
db.commit()

# 🚀 START (RASM + BUTTON)
@bot.on_message(filters.command("start"))
async def start(_, message):

    await message.reply_photo(
        photo="https://i.ibb.co/tpjt60kq/IMG-20260328-11432.jpg",
        caption="🎵 Salom! Qo‘shiq nomini yoz!",
        reply_markup=keyboard
    )

# 🎧 MUSIC SEARCH
@bot.on_message(filters.text & ~filters.regex("^/"))
async def music(_, message):

    query = message.text.lower().strip()
    msg = await message.reply("⏳ Qidirilyapti...")

    # CACHE
    cur.execute("SELECT file_id FROM songs WHERE name=?", (query,))
    data = cur.fetchone()

    if data:
        await message.reply_audio(data[0])
        await msg.delete()
        return

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                f"ytsearch1:{query}",
                download=True
            )

            if not info.get("entries"):
                await msg.edit("❌ Topilmadi!")
                return

            video = info["entries"][0]
            file_path = ydl.prepare_filename(video)

        sent = await message.reply_audio(
            file_path,
            caption=video["title"]
        )

        try:
            cur.execute(
                "INSERT OR REPLACE INTO songs (name, file_id) VALUES (?, ?)",
                (query, sent.audio.file_id)
            )
            db.commit()
        except:
            pass

        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ Xatolik!")

# 🚀 START BOT (CLEAN ENTRY POINT)
from pyrogram.idle import idle

def run_bot():
    async def main():
        await bot.start()
        print("🚀 Bot ishga tushdi")
        await idle()
        await bot.stop()

    bot.run(main)

if __name__ == "__main__":
    run_bot()
