import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import os
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

user_channels = {}
scheduled_posts = {}

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Buyruqlar:\n"
        "/addchannel - Kanal qoshish\n"
        "/post - Post yuborish\n"
        "/schedule - Vaqt belgilab post yuborish\n"
        "/check - Obunachi soni"
    )

@dp.message(Command("addchannel"))
async def add_channel(message: Message):
    await message.answer("Kanal username ini yuboring. Masalan: @mening_kanal")

@dp.message(Command("check"))
async def check_sub(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    channel = user_channels[user_id]
    try:
        count = await bot.get_chat_member_count(channel)
        await message.answer(f"Kanalingizda {count} ta obunachi bor!")
    except:
        await message.answer("Kanal topilmadi!")

@dp.message(F.text.startswith("@"))
async def save_channel(message: Message):
    user_id = message.from_user.id
    channel = message.text.strip()
    try:
        chat = await bot.get_chat(channel)
        user_channels[user_id] = channel
        await message.answer(f"✅ {chat.title} kanali qoshildi!")
    except:
        await message.answer("❌ Kanal topilmadi! Bot admin ekanligini tekshiring.")

@dp.message(Command("post"))
async def ask_post(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    await message.answer("Post matnini yozing:")

@dp.message(Command("schedule"))
async def ask_schedule(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    await message.answer(
        "Vaqt va matnni yuboring. Format:\n\n"
        "HH:MM | Post matni\n\n"
        "Masalan:\n"
        "18:00 | Assalomu alaykum!"
    )

@dp.message(F.text.contains("|"))
async def set_schedule(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    try:
        parts = message.text.split("|")
        time_str = parts[0].strip()
        post_text = parts[1].strip()
        hour, minute = map(int, time_str.split(":"))
        channel = user_channels[user_id]

        async def send_scheduled():
            await bot.send_message(channel, post_text)

        scheduler.add_job(
            send_scheduled,
            trigger="cron",
            hour=hour,
            minute=minute
        )

        await message.answer(f"✅ Post har kuni soat {time_str} da yuboriladi!")
    except:
        await message.answer("❌ Format xato! Masalan: 18:00 | Salom dunyo!")

@dp.message(F.text & ~F.text.startswith("/") & ~F.text.startswith("@") & ~F.text.contains("|"))
async def send_post(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        return
    channel = user_channels[user_id]
    try:
        await bot.send_message(channel, message.text)
        await message.answer("✅ Post yuborildi!")
    except:
        await message.answer("❌ Post yuborilmadi! Bot admin ekanligini tekshiring.")

@dp.message(Command("cancel"))
async def cancel_schedule(message: Message):
    jobs = scheduler.get_jobs()
    if not jobs:
        await message.answer("Hech qanday rejalashtirilgan post yo'q!")
        return
    scheduler.remove_all_jobs()
    await message.answer("✅ Barcha rejalashtirilgan postlar bekor qilindi!")
async def main():
    scheduler.start()
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)

asyncio.run(main())