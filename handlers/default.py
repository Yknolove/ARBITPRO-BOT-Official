from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# FSM-состояние для калькулятора Free версии
class FreeCalcState(StatesGroup):
    calc = State()

# Главное меню: выбор версии
def version_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free Version", callback_data="version:free")],
        [InlineKeyboardButton(text="💎 Pro Version", callback_data="version:pro")],
    ])

# Меню Free версии
def free_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="free:settings")],
        [InlineKeyboardButton(text="🧮 Калькулятор", callback_data="free:calc")],
        [InlineKeyboardButton(text="📊 Arbitrage", callback_data="free:arbitrage")],
        [InlineKeyboardButton(text="🔙 Вернуться", callback_data="version:main")],
    ])

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🆓 *Free Version* (Бесплатно):\n"
        "• Настройки биржи и пороги BUY/SELL (макс $100)\n"
        "• Калькулятор прибыли\n\n"
        "💎 *Pro Version* (Платно $12.99 USDT):\n"
        "• Всё из Free + история и топ-сделки\n"
        "• Архив сделок и расширенная статистика\n\n"
        "Выберите версию ниже:"   
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=version_menu())

@router.callback_query(lambda c: c.data.startswith("version:"))
async def cb_version(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "main":
        await c.message.edit_text(
            "Выберите версию ниже:", reply_markup=version_menu()
        )
    elif action == "free":
        await c.message.edit_text(
            "🆓 Free Version Menu:", reply_markup=free_menu()
        )
    elif action == "pro":
        await c.answer("Pro версия скоро будет доступна!", show_alert=True)
    await c.answer()

# Дальнейшие хендлеры Free версии остаются по аналогии...

