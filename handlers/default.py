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

# Инициализируем Router, чтобы main.py мог его импортировать
router = Router()

class FreeSettingsStates(StatesGroup):
    exchange = State()
    buy = State()
    sell = State()
    volume = State()

# Главное меню: выбор версии
def version_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free Version", callback_data="version:free")],
        [InlineKeyboardButton(text="💎 Pro Version", callback_data="version:pro")],
    ])

# Меню Free версии
def free_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏷 Биржа", callback_data="free:exchange")],
        [InlineKeyboardButton(text="📈 BUY", callback_data="free:buy")],
        [InlineKeyboardButton(text="📉 SELL", callback_data="free:sell")],
        [InlineKeyboardButton(text="🔢 Лимит", callback_data="free:volume")],
        [InlineKeyboardButton(text="📊 Показать настройки", callback_data="free:show")],
        [InlineKeyboardButton(text="🔙 Вернуться", callback_data="version:main")],
    ])

async def get_or_create_setting(session: AsyncSession, user_id: int) -> UserSetting:
    setting = await session.get(UserSetting, user_id)
    if not setting:
        setting = UserSetting(user_id=user_id)
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🆓 *Free Version* (Бесплатно):\n"
        "• Мониторинг одной биржи P2P\n"
        "• Порог BUY и SELL\n"
        "• Лимит объёма сделки\n\n"
        "💎 *Pro Version* (скоро): Расширенные функции"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=version_menu())

@router.callback_query(lambda c: c.data.startswith("version:"))
async def cb_version(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "main":
        await c.message.edit_text("Выберите версию:", reply_markup=version_menu())
    elif action == "free":
        await c.message.edit_text("🆓 Free меню:", reply_markup=free_menu())
    else:
        await c.answer("Pro версия скоро будет доступна!", show_alert=True)
    await c.answer()

@router.callback_query(lambda c: c.data.startswith("free:"))
async def cb_free(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "exchange":
        await c.message.edit_text("Введите биржу (binance, bybit, okx, bitget):")
        await state.set_state(FreeSettingsStates.exchange)
    elif action == "buy":
        await c.message.edit_text("Введите BUY-порог (число), например: 41.20")
        await state.set_state(FreeSettingsStates.buy)
    elif action == "sell":
        await c.message.edit_text("Введите SELL-порог (число), например: 42.50")
        await state.set_state(FreeSettingsStates.sell)
    elif action == "volume":
        await c.message.edit_text("Введите лимит объёма (число долларов)")
        await state.set_state(FreeSettingsStates.volume)
    elif action == "show":
        async with AsyncSessionLocal() as session:
            st = await get_or_create_setting(session, c.from_user.id)
        text = (
            f"📊 Настройки Free:\n"
            f"Биржа: {st.exchange}\n"
            f"BUY ≤ {st.buy_threshold or '-'}\n"
            f"SELL ≥ {st.sell_threshold or '-'}\n"
            f"Объём ≤ ${st.volume_limit or '-'}"
        )
        await c.message.edit_text(text, reply_markup=free_menu())
    elif action == "main":
        await c.message.edit_text("Выберите версию:", reply_markup=version_menu())
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
    await message.answer(f"✅ Биржа: {exch}", reply_markup=free_menu())

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
    await message.answer(f"✅ BUY ≤ {val}", reply_markup=free_menu())

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
    await message.answer(f"✅ SELL ≥ {val}", reply_markup=free_menu())

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
    await message.answer(f"✅ Объём ≤ ${val}", reply_markup=free_menu())
