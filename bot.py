from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run).start()
import os
import yt_dlp
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# 🔧 BOT SOZLAMALARI
ADMIN_ID = 7562363422  # Sizning Telegram IDingiz
BOT_TOKEN = "8331117123:AAE8BPC9yOrg8U839uVxC6Bf5BxXaL9o300"  # Bu yerga yangi tokeningizni qo'ying

bot = Client(
    "music_bot",
    bot_token=BOT_TOKEN,
    api_id=38920950,
    api_hash="1b2b3131134f901228acd5fa464c5eb5",
    sleep_threshold=60
)

# 📁 PAPKA
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# 📌 Foydalanuvchi tugmalari
keyboard = ReplyKeyboardMarkup(
    [["Qo‘shiq nomini yoz"]],
    resize_keyboard=True
)

# 📂 Obunachilar fayli
USER_FILE = "users.txt"
if not os.path.exists(USER_FILE):
    open(USER_FILE, "w").close()

# 🚀 /start komandasi
@bot.on_message(filters.command("start"))
async def start(client, message):
    # ID saqlash
    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())
    if str(message.from_user.id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{message.from_user.id}\n")

    # Admin uchun mini knopka
    if message.from_user.id == ADMIN_ID:
        admin_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("👁 Obunachilarni ko‘rish", callback_data="check_subs")],
                [InlineKeyboardButton("📢 Obunachilarga xabar", callback_data="broadcast")]
            ]
        )
    else:
        admin_buttons = None

    await message.reply_photo(
        photo="https://i.ibb.co/tpjt60kq/IMG-20260328-11432.jpg",
        caption="🎵 Salom! Men Azamat. Qo‘shiq nomini yoz 🎵",
        reply_markup=keyboard if admin_buttons is None else admin_buttons
    )

# 🔍 Qo‘shiq qidirish
@bot.on_message(filters.text & ~filters.regex("^/"))
async def find_song(client, message):
    if message.text == "Qo‘shiq nomini yoz":
        await message.reply("🎶 Qo‘shiq nomini yozing...")
        return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    loading = await message.reply_text("⏳ Qidirilyapti...")

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

    query = message.text
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
                task.cancel()
                await loading.edit("❌ Qo‘shiq topilmadi!")
                return

            video = info['entries'][0]
            file_path = ydl.prepare_filename(video)

        task.cancel()
        await loading.edit("🎧 Yuklanmoqda...")

        await message.reply_audio(file_path, caption=video['title'])

        os.remove(file_path)
        await loading.delete()

    except Exception as e:
        task.cancel()
        print(e)
        await loading.edit("❌ Xatolik yuz berdi!\nBoshqa qo‘shiq yozib ko‘ring.")

# 👁 Admin knopkalar
@bot.on_callback_query(filters.regex("check_subs"))
async def check_subs(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ Bu knopka sizga emas!", show_alert=True)
        return

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())
    subscriber_count = len(users)
    await callback_query.answer(f"👥 Obunachilar soni: {subscriber_count}", show_alert=True)

@bot.on_callback_query(filters.regex("broadcast"))
async def broadcast(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("❌ Bu knopka sizga emas!", show_alert=True)
        return

    with open(USER_FILE, "r") as f:
        users = set(f.read().splitlines())

    # Barcha obunachilarga xabar jo‘natish
    for user_id in users:
        try:
            await client.send_message(int(user_id), "📢 Bu admin xabari!")
        except:
            pass  # agar foydalanuvchi bloklagan bo‘lsa

    await callback_query.answer("✅ Xabar jo‘natildi", show_alert=True)

# ▶️ BOTNI ISHGA TUSHIRISH
bot.run()
