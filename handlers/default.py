from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# FSM для калькулятора во Free версии
class FreeCalcState(StatesGroup):
    calc = State()

# Главное меню: выбор версии
def version_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free Version", callback_data="version:free")],
        [InlineKeyboardButton(text="💎 Pro Version", callback_data="version:pro")],
    ])

# Меню Free версии
def free_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="free:settings")],
        [InlineKeyboardButton(text="🧮 Калькулятор", callback_data="free:calc")],
        [InlineKeyboardButton(text="📊 Arbitrage", callback_data="free:arbitrage")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="version:main")],
    ])

# Запуск бота
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Добро пожаловать в ArbitPRO! Выберите версию:", reply_markup=version_menu())

# Выбор версии
@router.callback_query(lambda c: c.data.startswith("version:"))
async def cb_version(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "main":
        await c.message.edit_text("Выберите версию:", reply_markup=version_menu())
    elif action == "free":
        await c.message.edit_text("🆓 Free Version Menu:", reply_markup=free_menu())
    elif action == "pro":
        await c.answer("Pro версия скоро будет доступна!", show_alert=True)
    await c.answer()

# Хендлеры Free версии
@router.callback_query(lambda c: c.data.startswith("free:"))
async def cb_free(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "settings":
        await c.message.edit_text("⚙️ Настройки Free версии (заглушка)", reply_markup=free_menu())
    elif action == "calc":
        await c.message.edit_text("Введите: amount buy_price sell_price\nПример: 100 41.20 42.50")
        await state.set_state(FreeCalcState.calc)
    elif action == "arbitrage":
        await c.message.edit_text("📊 Arbitrage Free (заглушка)", reply_markup=free_menu())
    await c.answer()

@router.message(FreeCalcState.calc)
async def process_free_calc(message: Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Ошибка: введите три числа через пробел.")
        return
    try:
        amt, bp, sp = map(float, parts)
    except ValueError:
        await message.answer("Неверный формат.")
        return
    profit = amt * (sp - bp)
    await state.clear()
    await message.answer(f"💰 Прибыль: {profit:.2f}₴", reply_markup=free_menu())
