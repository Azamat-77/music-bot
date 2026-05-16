import os
import sqlite3
import yt_dlp
from pyrogram import Client, filters, idle

# 🔧 CONFIG (buni keyin Render ENV ga chiqarib qo‘ygan yaxshi)
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

# START COMMAND
@bot.on_message(filters.command("start"))
def start(_, message):
    message.reply("🎵 Qo‘shiq nomini yoz!")

# MUSIC HANDLER
@bot.on_message(filters.text & ~filters.regex("^/"))
def music(_, message):

    q = message.text.lower().strip()
    msg = message.reply("⏳ Qidirilyapti...")

    # CACHE CHECK
    cur.execute("SELECT file_id FROM songs WHERE name=?", (q,))
    data = cur.fetchone()

    if data:
        message.reply_audio(data[0])
        msg.delete()
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
                msg.edit("❌ Topilmadi!")
                return

            video = info["entries"][0]
            file_path = ydl.prepare_filename(video)

        sent = message.reply_audio(file_path, caption=video["title"])

        try:
            cur.execute(
                "INSERT OR REPLACE INTO songs (name, file_id) VALUES (?, ?)",
                (q, sent.audio.file_id)
            )
            db.commit()
        except:
            pass

        msg.delete()

    except Exception as e:
        print(e)
        msg.edit("❌ Xatolik!")

# START BOT (FIXED - NO ASYNC)
if __name__ == "__main__":
    bot.start()
    print("🚀 Bot ishga tushdi")
    idle()
    bot.stop()
