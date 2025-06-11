from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

# Регистр сообщений меню: chat_id -> message_id
menu_registry: dict[int, int] = {}

router = Router()

class FreeSettingsStates(StatesGroup):
    exchange = State()
    buy = State()
    sell = State()
    volume = State()

def version_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🆓 Free Version", callback_data="version:free"),
        InlineKeyboardButton("💎 Pro Version", callback_data="version:pro")
    )
    return kb

def free_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🏷 Биржа", callback_data="free:exchange"),
        InlineKeyboardButton("📈 BUY ≤ ...", callback_data="free:buy"),
        InlineKeyboardButton("📉 SELL ≥ ...", callback_data="free:sell"),
        InlineKeyboardButton("🔢 Лимит", callback_data="free:volume"),
        InlineKeyboardButton("📊 Показать настройки", callback_data="free:show"),
        InlineKeyboardButton("🔙 Назад", callback_data="version:main")
    )
    return kb

async def get_or_create_setting(session: AsyncSession, user_id: int) -> UserSetting:
    st = await session.get(UserSetting, user_id)
    if not st:
        st = UserSetting(user_id=user_id)
        session.add(st)
        await session.commit()
        await session.refresh(st)
    return st

@router.message(Command("start"))
async def cmd_start(message: Message):
    sent = await message.answer(
        "👋 Добро пожаловать в ArbitPRO!\nВыберите версию:",
        reply_markup=version_menu()
    )
    menu_registry[sent.chat.id] = sent.message_id

@router.callback_query(lambda c: c.data.startswith("version:"))
async def cb_version(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":", 1)[1]
    if action == "main":
        text = "Выберите версию:"
        kb = version_menu()
    elif action == "free":
        text = "🆓 Free Version Menu:\n• Мониторинг одной биржи P2P\n• BUY/SELL пороги\n• Лимит объёма"
        kb = free_menu()
    else:
        await c.answer("Pro версия скоро будет доступна!", show_alert=True)
        return

    sent = await c.message.edit_text(text, reply_markup=kb)
    menu_registry[sent.chat.id] = sent.message_id
    await c.answer()

@router.callback_query(lambda c: c.data.startswith("free:"))
async def cb_free(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":", 1)[1]
    if action == "exchange":
        await c.message.edit_text("Введите биржу (binance, bybit, okx, bitget):")
        await state.set_state(FreeSettingsStates.exchange)
    elif action == "buy":
        await c.message.edit_text("Введите BUY-порог (число), например: 41.20:")
        await state.set_state(FreeSettingsStates.buy)
    elif action == "sell":
        await c.message.edit_text("Введите SELL-порог (число), например: 42.50:")
        await state.set_state(FreeSettingsStates.sell)
    elif action == "volume":
        await c.message.edit_text("Введите лимит объёма (число долларов):")
        await state.set_state(FreeSettingsStates.volume)
    elif action == "show":
        async with AsyncSessionLocal() as session:
            st = await get_or_create_setting(session, c.from_user.id)
        text = (
            f"📊 Настройки Free Version:\n"
            f"Биржа: {st.exchange}\n"
            f"BUY ≤ {st.buy_threshold or '-'}\n"
            f"SELL ≥ {st.sell_threshold or '-'}\n"
            f"Объём ≤ ${st.volume_limit or '-'}"
        )
        sent = await c.message.edit_text(text, reply_markup=free_menu())
        menu_registry[sent.chat.id] = sent.message_id
    elif action == "main":
        sent = await c.message.edit_text("Выберите версию:", reply_markup=version_menu())
        menu_registry[sent.chat.id] = sent.message_id

    await c.answer()

@router.message(FreeSettingsStates.exchange)
async def process_exchange(message: Message, state: FSMContext):
    exch = message.text.lower()
    if exch not in ("binance","bybit","okx","bitget"):
        return await message.answer("Неверная биржа.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.exchange = exch
        await session.commit()
    await state.clear()
    sent = await message.answer(f"✅ Биржа: {exch}", reply_markup=free_menu())
    menu_registry[sent.chat.id] = sent.message_id

@router.message(FreeSettingsStates.buy)
async def process_buy(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.buy_threshold = val
        await session.commit()
    await state.clear()
    sent = await message.answer(f"✅ BUY ≤ {val}", reply_markup=free_menu())
    menu_registry[sent.chat.id] = sent.message_id

@router.message(FreeSettingsStates.sell)
async def process_sell(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.sell_threshold = val
        await session.commit()
    await state.clear()
    sent = await message.answer(f"✅ SELL ≥ {val}", reply_markup=free_menu())
    menu_registry[sent.chat.id] = sent.message_id

@router.message(FreeSettingsStates.volume)
async def process_volume(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.volume_limit = val
        await session.commit()
    await state.clear()
    sent = await message.answer(f"✅ Объём ≤ ${val}", reply_markup=free_menu())
    menu_registry[sent.chat.id] = sent.message_id
