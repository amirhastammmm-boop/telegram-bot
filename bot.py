import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = "8283126628:AAEfCHJVqAZ8KuightbRkYQ8RtV5axz-bcc"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

DB_NAME = "vpn.db"


# ---------- DATABASE ----------
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            referral TEXT,
            invited_by TEXT,
            points INTEGER DEFAULT 0,
            sub_end TEXT,
            sub_gb INTEGER DEFAULT 0
        )
        """)
        await db.commit()


# ---------- MENU ----------
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 خرید اشتراک"), KeyboardButton(text="📦 اشتراک های من")],
            [KeyboardButton(text="⭐ امتیاز ها"), KeyboardButton(text="📚 آموزش استفاده")],
            [KeyboardButton(text="🆘 پشتیبانی")]
        ],
        resize_keyboard=True
    )


# ---------- START ----------
@dp.message(lambda m: m.text == "/start")
async def start(msg: types.Message):

    user_id = msg.from_user.id
    referral = f"REF{user_id}"

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        user = await cur.fetchone()

        if not user:
            await db.execute(
                "INSERT INTO users(user_id, referral) VALUES(?,?)",
                (user_id, referral)
            )
            await db.commit()

    await msg.answer("👋 خوش آمدی", reply_markup=main_menu())


# ---------- BUY ----------
@dp.message(lambda m: m.text == "🛒 خرید اشتراک")
async def buy_sub(msg: types.Message):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 یک ماهه | 33GB | 110T", url="https://testpay.ir/1")],
        [InlineKeyboardButton(text="🌟 دو ماهه | 71GB | 220T", url="https://testpay.ir/2")],
        [InlineKeyboardButton(text="🌟 سه ماهه | 110GB | 330T", url="https://testpay.ir/3")],
        [InlineKeyboardButton(text="⭐ با استفاده از امتیاز", callback_data="use_points")]
    ])

    await msg.answer("✨ انتخاب اشتراک", reply_markup=kb)


# ---------- USE POINTS ----------
@dp.callback_query(lambda c: c.data == "use_points")
async def use_points(call: types.CallbackQuery):

    user_id = call.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        points = (await cur.fetchone())[0]

    await call.message.answer(f"⭐ امتیاز شما: {points}")


# ---------- MY SUB ----------
@dp.message(lambda m: m.text == "📦 اشتراک های من")
async def my_sub(msg: types.Message):

    user_id = msg.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT sub_end, sub_gb FROM users WHERE user_id=?",
            (user_id,)
        )
        data = await cur.fetchone()

    await msg.answer(
        f"""
📦 اشتراک شما
⏳ تاریخ پایان: {data[0]}
📊 حجم باقی مانده: {data[1]} GB
"""
    )


# ---------- POINTS ----------
@dp.message(lambda m: m.text == "⭐ امتیاز ها")
async def points(msg: types.Message):

    user_id = msg.from_user.id

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT points, referral FROM users WHERE user_id=?",
            (user_id,)
        )
        data = await cur.fetchone()

    await msg.answer(
        f"""
⭐ امتیاز شما: {data[0]}
👥 کد دعوت شما:
<code>{data[1]}</code>
"""
    )


# ---------- TRAIN ----------
@dp.message(lambda m: m.text == "📚 آموزش استفاده")
async def train(msg: types.Message):

    await msg.answer("📥 فایل آموزش")

    await bot.send_document(msg.chat.id, types.FSInputFile("v2ray.txt"))
    await bot.send_document(msg.chat.id, types.FSInputFile("wireguard.txt"))


# ---------- SUPPORT ----------
@dp.message(lambda m: m.text == "🆘 پشتیبانی")
async def support(msg: types.Message):

    await msg.answer("🆔 پشتیبانی : 633464148")


# ---------- RUN ----------
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
