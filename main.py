# main.py
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.session import AiohttpSession, DefaultBotProperties
import asyncio

API_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

# Инициализация бота
session = AiohttpSession()
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"), session=session)
dp = Dispatcher()

# Настройка главного меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🆓 Free Version")],
        [KeyboardButton("⚙️ Settings")],
    ],
    resize_keyboard=True,
    is_persistent=True,
    input_field_placeholder="Выберите раздел",
)

@dp.message.register(commands=["start"])
async def cmd_start(message: Message):
    await message.answer(
        text=(
            "👋 Добро пожаловать!\n"
            "<b>Free Version:</b> мониторинг одной биржи P2P (Binance, Bybit, OKX, Bitget).\n"
            "Введите /help для инструкций."
        ),
        reply_markup=main_kb
    )

@dp.message.register(lambda m: m.text == "🆓 Free Version")
async def free_version(message: Message):
    await message.answer(
        text="Вы выбрали Free Version. Выберите биржу:\n/binance, /bybit, /okx, /bitget",
        reply_markup=main_kb
    )

@dp.message.register(commands=["binance", "bybit", "okx", "bitget"])
async def select_exchange(message: Message):
    exch = message.text.lstrip("/").capitalize()
    await message.answer(f"Настроен мониторинг биржи: {exch}", reply_markup=main_kb)

@dp.message.register(lambda m: m.text == "⚙️ Settings")
async def settings(message: Message):
    await message.answer("Настройки пока недоступны.", reply_markup=main_kb)

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
