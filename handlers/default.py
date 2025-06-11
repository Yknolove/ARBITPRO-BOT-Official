from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# FSM-состояния для настроек и калькулятора
class BotStates(StatesGroup):
    exchange = State()
    buy = State()
    sell = State()
    calc = State()

# Главное меню — Inline-клавиатура
MAIN_INLINE = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="show_settings"),
        InlineKeyboardButton(text="🏷 Биржа", callback_data="set_exchange")
    ],
    [
        InlineKeyboardButton(text="📈 BUY", callback_data="set_buy"),
        InlineKeyboardButton(text="📉 SELL", callback_data="set_sell")
    ],
    [InlineKeyboardButton(text="🧮 Калькулятор", callback_data="set_calc")],
    [
        InlineKeyboardButton(text="📜 История", callback_data="show_history"),
        InlineKeyboardButton(text="🔥 Топ-сделки", callback_data="show_top")
    ],
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
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO! Выберите опцию:",
        reply_markup=MAIN_INLINE
    )

@router.callback_query(lambda c: c.data == "show_settings")
async def cb_show_settings(c: CallbackQuery):
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, c.from_user.id)
    text = (
        f"📊 Текущие настройки:\n"
        f"• Биржа: {st.exchange}\n"
        f"• BUY ≤ {st.buy_threshold or '-'}\n"
        f"• SELL ≥ {st.sell_threshold or '-'}"
    )
    await c.message.edit_text(text, reply_markup=MAIN_INLINE)
    await c.answer()

@router.callback_query(lambda c: c.data == "set_exchange")
async def cb_set_exchange(c: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.exchange)
    await c.message.edit_text("Введите биржу (binance, bybit или bitget):")
    await c.answer()

@router.message(BotStates.exchange)
async def process_exchange(message: Message, state: FSMContext):
    exch = message.text.lower()
    if exch not in ("binance", "bybit", "bitget"):
        return await message.answer("Неверная биржа, попробуйте снова.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.exchange = exch
        await session.commit()
    await state.clear()
    await message.answer(f"✅ Биржа установлена: {exch}", reply_markup=MAIN_INLINE)

@router.callback_query(lambda c: c.data == "set_buy")
async def cb_set_buy(c: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.buy)
    await c.message.edit_text("Введите BUY-порог (число), например: 41.20")
    await c.answer()

@router.message(BotStates.buy)
async def process_buy(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат, введите число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.buy_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ BUY-порог установлен: ≤ {val}", reply_markup=MAIN_INLINE)

@router.callback_query(lambda c: c.data == "set_sell")
async def cb_set_sell(c: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.sell)
    await c.message.edit_text("Введите SELL-порог (число), например: 42.50")
    await c.answer()

@router.message(BotStates.sell)
async def process_sell(message: Message, state: FSMContext):
    try:
        val = float(message.text)
    except ValueError:
        return await message.answer("Неверный формат, введите число.")
    async with AsyncSessionLocal() as session:
        st = await get_or_create_setting(session, message.from_user.id)
        st.sell_threshold = val
        await session.commit()
    await state.clear()
    await message.answer(f"✅ SELL-порог установлен: ≥ {val}", reply_markup=MAIN_INLINE)

@router.callback_query(lambda c: c.data == "set_calc")
async def cb_set_calc(c: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.calc)
    await c.message.edit_text("Введите: amount buy_price sell_price, например: 100 41.20 42.50")
    await c.answer()

@router.message(BotStates.calc)
async def process_calc(message: Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Неверный формат ввода.", reply_markup=MAIN_INLINE)
        return
    try:
        amount, buy_p, sell_p = map(float, parts)
    except ValueError:
        await message.answer("Введите корректные числа.", reply_markup=MAIN_INLINE)
        return
    profit = amount * (sell_p - buy_p)
    await state.clear()
    await message.answer(f"💰 Прибыль: {profit:.2f}₴", reply_markup=MAIN_INLINE)

@router.callback_query(lambda c: c.data == "show_history")
async def cb_show_history(c: CallbackQuery):
    await c.message.edit_text("🕑 История сделок: (заглушка)", reply_markup=MAIN_INLINE)
    await c.answer()

@router.callback_query(lambda c: c.data == "show_top")
async def cb_show_top(c: CallbackQuery):
    await c.message.edit_text("🏆 Топ-сделки: (заглушка)", reply_markup=MAIN_INLINE)
    await c.answer()
