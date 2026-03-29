import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TOKEN")
KANAL = "@youtube_banners_logos"

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

user_channels = {}

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(KANAL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def sub_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Obuna bo'lish", url=f"https://t.me/{KANAL[1:]}")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ])

@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer("⚠️ Botdan foydalanish uchun kanalga obuna bo'ling!", reply_markup=sub_keyboard())
        return
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Buyruqlar:\n"
        "/addchannel - Kanal qoshish\n"
        "/post - Matn post yuborish\n"
        "/photo - Rasm yuborish\n"
        "/video - Video yuborish\n"
        "/schedule - Vaqt belgilab post yuborish\n"
        "/cancel - Rejalashtirishni bekor qilish\n"
        "/check - Obunachi soni"
    )

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery):
    user_id = call.from_user.id
    if await check_subscription(user_id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Endi botdan foydalanishingiz mumkin!\n\n/start yozing!")
    else:
        await call.answer("❌ Siz hali obuna bo'lmagansiz!", show_alert=True)

@dp.message(Command("addchannel"))
async def add_channel(message: Message):
    await message.answer("Kanal username ini yuboring. Masalan: @mening_kanal")

@dp.message(Command("check"))
async def check_count(message: Message):
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

@dp.message(Command("photo"))
async def ask_photo(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    await message.answer("Rasmni yuboring:")

@dp.message(Command("video"))
async def ask_video(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    await message.answer("Videoni yuboring:")

@dp.message(Command("schedule"))
async def ask_schedule(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    await message.answer("Vaqt va matnni yuboring:\n\nHH:MM | Post matni\n\nMasalan:\n18:00 | Salom!")

@dp.message(Command("cancel"))
async def cancel_schedule(message: Message):
    jobs = scheduler.get_jobs()
    if not jobs:
        await message.answer("Hech qanday rejalashtirilgan post yo'q!")
        return
    scheduler.remove_all_jobs()
    await message.answer("✅ Barcha rejalashtirilgan postlar bekor qilindi!")

@dp.message(F.photo)
async def send_photo(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    channel = user_channels[user_id]
    try:
        photo = message.photo[-1].file_id
        caption = message.caption or ""
        await bot.send_photo(channel, photo, caption=caption)
        await message.answer("✅ Rasm kanalga yuborildi!")
    except:
        await message.answer("❌ Rasm yuborilmadi! Bot admin ekanligini tekshiring.")

@dp.message(F.video)
async def send_video(message: Message):
    user_id = message.from_user.id
    if user_id not in user_channels:
        await message.answer("Avval /addchannel bilan kanal qoshing!")
        return
    channel = user_channels[user_id]
    try:
        video = message.video.file_id
        caption = message.caption or ""
        await bot.send_video(channel, video, caption=caption)
        await message.answer("✅ Video kanalga yuborildi!")
    except:
        await message.answer("❌ Video yuborilmadi! Bot admin ekanligini tekshiring.")

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

        scheduler.add_job(send_scheduled, trigger="cron", hour=hour, minute=minute)
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
        await message.answer("❌ Post yuborilmadi!")

async def main():
    scheduler.start()
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)

asyncio.run(main())

```