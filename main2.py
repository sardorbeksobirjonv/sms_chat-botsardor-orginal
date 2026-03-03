import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

# ⚙️ BOT MA'LUMOTLARI
BOT_TOKEN = "8657747765:AAH9tI67E9gX5vYklYeNlzPLbyssEBubM6E"
ADMIN_ID = 7752032178  

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=BOT_TOKEN)

# 🧠 HOLATLAR
class ReplyState(StatesGroup):
    waiting_for_reply = State()

# 🚀 /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        f"🤝 <b>{message.from_user.full_name}</b>, yozishingiz mumkin.\n\n"
        "⏳ Tez orada javob beraman."
    )
    await message.answer(text, parse_mode="HTML")

# 💬 Foydalanuvchi xabar yuborganda (matn, rasm, ovoz va boshqalar)
@dp.message(lambda msg: msg.from_user.id != ADMIN_ID)
async def forward_all_to_admin(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    text_info = f"👤 <b>Foydalanuvchi:</b> {user_name}\n🆔 <code>{user_id}</code>\n━━━━━━━━━━━━━━━"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Javob yozish", callback_data=f"reply_{user_id}")]
        ]
    )

    try:
        # Matn
        if message.text:
            await bot.send_message(
                ADMIN_ID,
                f"📩 <b>Yangi matn xabar:</b>\n\n{text_info}\n💬 {message.text}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        # Rasm
        elif message.photo:
            file_id = message.photo[-1].file_id
            await bot.send_photo(
                ADMIN_ID, file_id,
                caption=f"🖼 <b>Rasm yuborildi!</b>\n\n{text_info}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        # Video
        elif message.video:
            await bot.send_video(
                ADMIN_ID, message.video.file_id,
                caption=f"🎬 <b>Video yuborildi!</b>\n\n{text_info}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        # Ovozli xabar (voice)
        elif message.voice:
            await bot.send_voice(
                ADMIN_ID, message.voice.file_id,
                caption=f"🎙 <b>Ovozli xabar!</b>\n\n{text_info}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        # Audio fayl
        elif message.audio:
            await bot.send_audio(
                ADMIN_ID, message.audio.file_id,
                caption=f"🎧 <b>Audio yuborildi!</b>\n\n{text_info}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        # Stiker
        elif message.sticker:
            await bot.send_sticker(ADMIN_ID, message.sticker.file_id)
            await bot.send_message(
                ADMIN_ID,
                f"💠 <b>Stiker yuborildi!</b>\n\n{text_info}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await message.answer("❗ Yuborgan fayl turi qo‘llab-quvvatlanmaydi.")

        await message.answer(
            "✅ Xabaringiz Sardorbekga yuborildi!\n"
            "🕐 Yana savol yozishingiz mumkin."
        )

    except Exception as e:
        print(f"❌ Foydalanuvchi xabarini yuborishda xato: {e}")

# 🧑‍💻 Admin “javob yozish” bosganda
@dp.callback_query(lambda c: c.data.startswith("reply_"))
async def reply_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    await state.update_data(target_user=user_id)
    
    await callback_query.message.answer(
        f"✍️ <b>Javob yozing yoki ovozli xabar yuboring.</b>\n"
        f"🎯 Foydalanuvchi ID: <code>{user_id}</code>",
        parse_mode="HTML"
    )
    await state.set_state(ReplyState.waiting_for_reply)
    await callback_query.answer()

# 📤 Admin javob yuborganda (matn, ovoz, rasm va boshqalar)
@dp.message(ReplyState.waiting_for_reply)
async def send_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("target_user")

    if not user_id:
        await message.answer("⚠️ Foydalanuvchi topilmadi.")
        await state.clear()
        return

    try:
        if message.text:
            await bot.send_message(
                user_id,
                f"📨 <b>Sardorbek javobi:</b>\n\n{message.text}",
                parse_mode="HTML"
            )
        elif message.voice:
            await bot.send_voice(
                user_id,
                message.voice.file_id,
                caption="🎧 Sardorbekdan ovozli javob"
            )
        elif message.audio:
            await bot.send_audio(
                user_id,
                message.audio.file_id,
                caption="🎵 Sardorbekdan audio javob"
            )
        elif message.photo:
            await bot.send_photo(
                user_id,
                message.photo[-1].file_id,
                caption="🖼 Sardorbek rasm yubordi"
            )
        elif message.video:
            await bot.send_video(
                user_id,
                message.video.file_id,
                caption="🎬 Sardorbek video yubordi"
            )
        else:
            await message.answer("❗ Ushbu turdagi faylni yuborib bo‘lmaydi.")
            return

        await message.answer("✅ Javob foydalanuvchiga muvaffaqiyatli yuborildi!")

    except TelegramForbiddenError:
        await message.answer("🚫 Foydalanuvchi botni bloklagan.")
    except TelegramBadRequest:
        await message.answer("⚠️ Xatolik: foydalanuvchiga yuborishda muammo.")
    except Exception as e:
        await message.answer(f"❌ Xato yuz berdi: {e}")

    await state.clear()

# 🔄 Botni ishga tushirish
async def main():
    print("🤖 Bot ishga tushdi → Sardorbek support bot online 🛰️")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())