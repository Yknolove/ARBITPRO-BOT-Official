from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.state import State
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

class BotStates(StatesGroup):
    exchange = State()
    buy = State()
    sell = State()
    calc = State()

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🧮 Калькулятор")],
        [KeyboardButton(text="🏷 Установить биржу"), KeyboardButton(text="📈 BUY"), KeyboardButton(text="📉 SELL")],
        [KeyboardButton(text="📜 История"), KeyboardButton(text="🔥 Топ-сделки")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def get_or_create_setting(session: AsyncSession, user_id: int) -> UserSetting:
    setting = await session.get(UserSetting, user_id)
    if not setting:
        setting = UserSetting(user_id=user_id)
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting

@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Добро пожаловать в ArbitPRO! Выберите опцию:", reply_markup=MAIN_KB)

@router.message(lambda message: message.text == "⚙️ Настройки")
async def show_settings(message: types.Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
    await message.answer(
        f"📊 Настройки:\nБиржа: {st.exchange}\nBUY ≤ {st.buy_threshold or '-'}\nSELL ≥ {st.sell_threshold or '-'}",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text == "🏷 Установить биржу")
async def set_exchange_start(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.exchange)
    await message.answer("Введите биржу (binance, bybit или bitget):", reply_markup=ReplyKeyboardRemove())

@router.message(BotStates.exchange)
async def process_exchange(message: types.Message, state: FSMContext):
    exch = message.text.lower()
    if exch not in ("binance", "bybit", "bitget"):
        return await message.answer("Неверная биржа. Введите: binance, bybit или bitget.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.exchange = exch
        await session.commit()
    await state.clear()
    await message.answer(f"✅ Биржа установлена: {exch}", reply_markup=MAIN_KB)

@router.message(lambda message: message.text == "📈 BUY")
async def set_buy_start(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.buy)
    await message.answer("Введите BUY-порог (число), например: 41.20", reply_markup=ReplyKeyboardRemove())

@router.message(BotStates.buy)
async def process_buy(message: types.Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат. Введите число: 41.20.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.buy_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ BUY-порог установлен: ≤ {val}", reply_markup=MAIN_KB)

@router.message(lambda message: message.text == "📉 SELL")
async def set_sell_start(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.sell)
    await message.answer("Введите SELL-порог (число), например: 42.50", reply_markup=ReplyKeyboardRemove())

@router.message(BotStates.sell)
async def process_sell(message: types.Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат. Введите число: 42.50.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.sell_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ SELL-порог установлен: ≥ {val}", reply_markup=MAIN_KB)

@router.message(lambda message: message.text == "🧮 Калькулятор")
async def set_calc_start(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.calc)
    await message.answer("Введите: сумма buy_price sell_price, например: 100 41.20 42.50", reply_markup=ReplyKeyboardRemove())

@router.message(BotStates.calc)
async def process_calc(message: types.Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("Ошибка ввода. Введите три числа через пробел.", reply_markup=MAIN_KB)
    try:
        amount, buy_p, sell_p = map(float, parts)
    except ValueError:
        return await message.answer("Введите числа, например: 100 41.20 42.50.", reply_markup=MAIN_KB)
    profit = amount * (sell_p - buy_p)
    await state.clear()
    await message.answer(f"💰 Прибыль: {profit:.2f}₴", reply_markup=MAIN_KB)

@router.message(lambda message: message.text == "📜 История")
async def text_history(message: types.Message):
    await message.answer("🕑 История сделок: (заглушка)", reply_markup=MAIN_KB)

@router.message(lambda message: message.text == "🔥 Топ-сделки")
async def text_top(message: types.Message):
    await message.answer("🏆 Топ-сделки: (заглушка)", reply_markup=MAIN_KB)

