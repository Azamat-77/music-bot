import os
import sqlite3
import yt_dlp
from pyrogram import Client, filters
from pyrogram.idle import idle

# 🔧 CONFIG
API_ID = 38920950
API_HASH = "1b2b3131134f901228acd5fa464c5eb5"
BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"

bot = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)

# DATABASE
db = sqlite3.connect("music.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    name TEXT UNIQUE,
    file_id TEXT
)
""")
db.commit()

# START
@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("🎵 Qo‘shiq nomini yoz!")

# MUSIC
@bot.on_message(filters.text & ~filters.regex("^/"))
async def music(_, message):

    q = message.text.lower().strip()
    msg = await message.reply("⏳ Qidirilyapti...")

    # CACHE
    cur.execute("SELECT file_id FROM songs WHERE name=?", (q,))
    data = cur.fetchone()

    if data:
        await message.reply_audio(data[0])
        await msg.delete()
        return

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{q}", download=True)

            if not info.get("entries"):
                await msg.edit("❌ Topilmadi!")
                return

            video = info["entries"][0]
            file_path = ydl.prepare_filename(video)

        sent = await message.reply_audio(file_path, caption=video["title"])

        try:
            cur.execute(
                "INSERT OR REPLACE INTO songs (name, file_id) VALUES (?, ?)",
                (q, sent.audio.file_id)
            )
            db.commit()
        except:
            pass

        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ Xatolik!")

# RUN (FINAL FIX)
async def main():
    await bot.start()
    print("🚀 Bot ishga tushdi")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    bot.run(main)
