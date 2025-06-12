from aiogram import Router
from aiogram.filters.text import Text
from aiogram.filters.command import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    Message, ReplyKeyboardRemove
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

class FreeSettingsStates(StatesGroup):
    exchange = State()
    buy      = State()
    sell     = State()
    volume   = State()

# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆓 Free Version")],
        [KeyboardButton(text="💎 Pro Version")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Меню Free-версии
free_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏷 Биржа"), KeyboardButton(text="📈 BUY")],
        [KeyboardButton(text="📉 SELL"),  KeyboardButton(text="🔢 Лимит")],
        [KeyboardButton(text="📊 Показать настройки"), KeyboardButton(text="🔙 Главное меню")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def get_or_create_setting(session: AsyncSession, user_id: int) -> UserSetting:
    st = await session.get(UserSetting, user_id)
    if not st:
        st = UserSetting(user_id=user_id)
        session.add(st)
        await session.commit()
        await session.refresh(st)
    return st

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO!\nВыберите версию:",
        reply_markup=main_kb
    )

@router.message(Text(equals="🆓 Free Version"))
async def enter_free(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🆓 Free Version Menu:\nВыберите действие:",
        reply_markup=free_kb
    )

@router.message(Text(equals="💎 Pro Version"))
async def enter_pro(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "💎 Pro версия скоро будет доступна!",
        reply_markup=main_kb
    )

@router.message(Text(equals="🔙 Главное меню"))
async def back_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы вернулись в главное меню:",
        reply_markup=main_kb
    )

@router.message(Text(equals="🏷 Биржа"))
async def set_exchange_prompt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Введите биржу (binance, bybit, okx, bitget):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FreeSettingsStates.exchange)

@router.message(FreeSettingsStates.exchange)
async def process_exchange(message: Message, state: FSMContext):
    exch = message.text.lower()
    if exch not in ("binance", "bybit", "okx", "bitget"):
        return await message.answer("Неверная биржа.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.exchange = exch
        await session.commit()
    await state.clear()
    await message.answer(f"✅ Биржа установлена: {exch}", reply_markup=free_kb)

@router.message(Text(equals="📈 BUY"))
async def set_buy_prompt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Введите BUY-порог (число), например: 41.20:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FreeSettingsStates.buy)

@router.message(FreeSettingsStates.buy)
async def process_buy(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат. Введите число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.buy_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ BUY ≤ {val}", reply_markup=free_kb)

@router.message(Text(equals="📉 SELL"))
async def set_sell_prompt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Введите SELL-порог (число), например: 42.50:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FreeSettingsStates.sell)

@router.message(FreeSettingsStates.sell)
async def process_sell(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат. Введите число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.sell_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ SELL ≥ {val}", reply_markup=free_kb)

@router.message(Text(equals="🔢 Лимит"))
async def set_volume_prompt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Введите лимит объёма (число долларов):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FreeSettingsStates.volume)

@router.message(FreeSettingsStates.volume)
async def process_volume(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат. Введите число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.volume_limit = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ Объём ≤ ${val}", reply_markup=free_kb)

@router.message(Text(equals="📊 Показать настройки"))
async def show_settings(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
    await message.answer(
        f"📊 Настройки Free Version:\n"
        f"Биржа: {st.exchange}\n"
        f"BUY ≤ {st.buy_threshold or '-'}\n"
        f"SELL ≥ {st.sell_threshold or '-'}\n"
        f"Объём ≤ ${st.volume_limit or '-'}",
        reply_markup=free_kb
    )
