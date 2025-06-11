from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# FSM-состояния для ввода порогов
class ConfigStates(StatesGroup):
    waiting_buy = State()
    waiting_sell = State()
    waiting_exchange = State()

# Главное меню — Inline
MAIN_MENU = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
    [InlineKeyboardButton(text="ℹ️ Показать настройки", callback_data="menu_show")],
])

# Подменю настроек
SETTINGS_MENU = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📈 Установить BUY-порог", callback_data="set_buy")],
    [InlineKeyboardButton(text="📉 Установить SELL-порог", callback_data="set_sell")],
    [InlineKeyboardButton(text="🏷 Выбрать биржу", callback_data="set_exchange")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")],
])

async def get_setting(session: AsyncSession, user_id: int) -> UserSetting:
    setting = await session.get(UserSetting, user_id)
    if not setting:
        setting = UserSetting(user_id=user_id)
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting

@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO!\n\n"
        "Здесь можно быстро настроить фильтры и получать уведомления об арбитраже.",
        reply_markup=MAIN_MENU
    )

@router.callback_query(lambda c: c.data == "menu_show")
async def show_settings(c: types.CallbackQuery):
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, c.from_user.id)
    await c.message.edit_text(
        f"📊 Текущие настройки:\n"
        f"• Биржа: <b>{setting.exchange}</b>\n"
        f"• Buy ≤ <b>{setting.buy_threshold or '—'}</b>\n"
        f"• Sell ≥ <b>{setting.sell_threshold or '—'}</b>",
        parse_mode="HTML",
        reply_markup=MAIN_MENU
    )
    await c.answer()

@router.callback_query(lambda c: c.data == "menu_settings")
async def menu_settings(c: types.CallbackQuery):
    await c.message.edit_text("⚙️ Выберите, что изменить:", reply_markup=SETTINGS_MENU)
    await c.answer()

@router.callback_query(lambda c: c.data == "back_main")
async def back_main(c: types.CallbackQuery):
    await c.message.edit_text("Главное меню:", reply_markup=MAIN_MENU)
    await c.answer()

@router.callback_query(lambda c: c.data == "set_buy")
async def callback_set_buy(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer("Введите новый BUY-порог (например: 41.20):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ConfigStates.waiting_buy)
    await c.answer()

@router.callback_query(lambda c: c.data == "set_sell")
async def callback_set_sell(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer("Введите новый SELL-порог (например: 42.50):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ConfigStates.waiting_sell)
    await c.answer()

@router.callback_query(lambda c: c.data == "set_exchange")
async def callback_set_exchange(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer("Введите биржу (binance, bybit или bitget):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ConfigStates.waiting_exchange)
    await c.answer()

@router.message(ConfigStates.waiting_buy)
async def process_buy(message: types.Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат, введите число, например: 41.20")
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.buy_threshold = val
        await session.commit()
    await message.answer(f"✅ BUY-порог установлен: ≤ {val}", reply_markup=MAIN_MENU)
    await state.clear()

@router.message(ConfigStates.waiting_sell)
async def process_sell(message: types.Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат, введите число, например: 42.50")
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.sell_threshold = val
        await session.commit()
    await message.answer(f"✅ SELL-порог установлен: ≥ {val}", reply_markup=MAIN_MENU)
    await state.clear()

@router.message(ConfigStates.waiting_exchange)
async def process_exchange(message: types.Message, state: FSMContext):
    exch = message.text.lower()
    if exch not in ("binance", "bybit", "bitget"):
        return await message.answer("Неверная биржа, введите: binance, bybit или bitget")
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.exchange = exch
        await session.commit()
    await message.answer(f"✅ Биржа установлена: {exch}", reply_markup=MAIN_MENU)
    await state.clear()
