from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting
from services.aggregator import fetch_current_arbitrage  # нужно реализовать или stub

router = Router()

# FSM-состояния
class SettingsStates(StatesGroup):
    exchange = State()
    buy = State()
    sell = State()

class CalcStates(StatesGroup):
    calc = State()

# Меню
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
         InlineKeyboardButton(text="🧮 Калькулятор", callback_data="menu:calc")],
        [InlineKeyboardButton(text="📊 Связки", callback_data="menu:arbitrage"),
         InlineKeyboardButton(text="📜 История", callback_data="menu:history")],
        [InlineKeyboardButton(text="🔥 Топ", callback_data="menu:top")],
    ])

def settings_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷 Биржа", callback_data="settings:exchange"),
         InlineKeyboardButton(text="📈 BUY", callback_data="settings:buy")],
        [InlineKeyboardButton(text="📉 SELL", callback_data="settings:sell"),
         InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main")],
    ])

# Другие подменю
def arbitrage_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="arbitrage:refresh"),
         InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main")],
    ])

stubs_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main")]
])

async def get_or_create_setting(session: AsyncSession, user_id: int) -> UserSetting:
    st = await session.get(UserSetting, user_id)
    if not st:
        st = UserSetting(user_id=user_id)
        session.add(st)
        await session.commit()
        await session.refresh(st)
    return st

# Обработчики
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Добро пожаловать в ArbitPRO!", reply_markup=main_menu())

@router.callback_query(lambda c: c.data.startswith("menu:"))
async def cb_main(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "main":
        await c.message.edit_text("Главное меню:", reply_markup=main_menu())
    elif action == "settings":
        await c.message.edit_text("Настройки:", reply_markup=settings_menu())
    elif action == "calc":
        await c.message.edit_text(
            "🧮 Калькулятор: введите amount buy_price sell_price",
            reply_markup=None
        )
        await state.set_state(CalcStates.calc)
    elif action == "arbitrage":
        rates = await fetch_current_arbitrage()
        text = "\n".join(
            f"{exch.title()}: buy {r['buy']} sell {r['sell']}" for exch, r in rates.items()
        )
        await c.message.edit_text(text or "Нет данных", reply_markup=arbitrage_menu())
    elif action == "history":
        await c.message.edit_text("📜 История: заглушка", reply_markup=stubs_menu)
    elif action == "top":
        await c.message.edit_text("🔥 Топ: заглушка", reply_markup=stubs_menu)
    await c.answer()

@router.callback_query(lambda c: c.data.startswith("settings:"))
async def cb_settings(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "exchange":
        await c.message.edit_text("Введите биржу (binance, bybit, bitget):")
        await state.set_state(SettingsStates.exchange)
    elif action == "buy":
        await c.message.edit_text("Введите BUY-порог (число):")
        await state.set_state(SettingsStates.buy)
    elif action == "sell":
        await c.message.edit_text("Введите SELL-порог (число):")
        await state.set_state(SettingsStates.sell)
    await c.answer()

@router.message(SettingsStates.exchange)
async def process_exchange(message: Message, state: FSMContext):
    exch = message.text.lower()
    if exch not in ("binance","bybit","bitget"):
        return await message.answer("Неверная биржа.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.exchange = exch
        await session.commit()
    await state.clear()
    await message.answer(f"✅ Биржа: {exch}", reply_markup=main_menu())

@router.message(SettingsStates.buy)
async def process_buy(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except:
        return await message.answer("Не число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.buy_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ BUY ≤ {val}", reply_markup=main_menu())

@router.message(SettingsStates.sell)
async def process_sell(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except:
        return await message.answer("Не число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.sell_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ SELL ≥ {val}", reply_markup=main_menu())

@router.message(CalcStates.calc)
async def process_calc(message: Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("Ошибка, три числа.", reply_markup=main_menu())
    try:
        amt, bp, sp = map(float, parts)
    except:
        return await message.answer("Не числа.", reply_markup=main_menu())
    profit = amt * (sp - bp)
    await state.clear()
    await message.answer(f"💰 Прибыль: {profit:.2f}₴", reply_markup=main_menu())
