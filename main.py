# main.py
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

API_TOKEN = "YOUR_TOKEN_HERE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Команда /start — показывает выбор Free / Pro версии
@dp.message(commands=["start"])
async def cmd_start(message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free Version", callback_data="version:free")],
        [InlineKeyboardButton(text="⭐ Pro Version", callback_data="version:pro")],
    ])
    await message.answer("Выберите версию:", reply_markup=kb)

# Обработка выбранной версии
@dp.callback_query(lambda c: c.data and c.data.startswith("version:"))
async def cb_version(c: CallbackQuery):
    version = c.data.split(":")[1]
    text = "Free Version:\n— Мониторинг 1 биржи P2P (Binance/Bybit/OKX/Bitget)\n— Минимум настроек\nБез калькулятора и лимитов."
    await c.message.edit_text(text, reply_markup=free_menu_kb())
    await c.answer()

# Меню Free‑версии
def free_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Установить биржу", callback_data="free:set_exchange")
    builder.button(text="🔄 Обновить курс", callback_data="free:refresh")
    builder.adjust(1)  # 1 кнопка в ряд
    return builder.as_markup()

# Обработчики Free‑меню
@dp.callback_query(lambda c: c.data == "free:set_exchange")
async def cb_set_exchange(c: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Binance", callback_data="exchange:binance")],
        [InlineKeyboardButton("Bybit", callback_data="exchange:bybit")],
        [InlineKeyboardButton("OKX",    callback_data="exchange:okx")],
        [InlineKeyboardButton("Bitget",callback_data="exchange:bitget")],
        [InlineKeyboardButton("◀️ Назад", callback_data="version:free")],
    ])
    await c.message.edit_text("Выберите биржу для мониторинга:", reply_markup=kb)
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("exchange:"))
async def cb_exchange(c: CallbackQuery):
    exch = c.data.split(":")[1]
    # здесь сохраняем выбор пользователя в БД/памяти
    await c.answer(f"Выбрана биржа: {exch.capitalize()}")
    await c.message.edit_text(f"Мониторинг {exch.capitalize()} активирован.\nИспользуй 🔄 для обновления курса.", reply_markup=free_menu_kb())

@dp.callback_query(lambda c: c.data == "free:refresh")
async def cb_refresh(c: CallbackQuery):
    # здесь <<fetch_rates>> — твоя функция, возвращающая rate
    rate = fetch_rates_for_user(c.from_user.id)  # stub, реализуй сам
    await c.answer("Курс обновлён")
    await c.message.edit_text(f"Текущий курс: {rate}", reply_markup=free_menu_kb())

# Заглушка — реализация ф-ии
def fetch_rates_for_user(user_id):
    return "41.50 / 42.60"  # пример

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
