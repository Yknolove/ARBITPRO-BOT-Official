from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# FSM-состояния для Калькулятора
class CalcStates(StatesGroup):
    waiting_input = State()

# Постоянное меню снизу
MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⚙️ Настройки"),
            KeyboardButton(text="🧮 Калькулятор"),
        ],
        [
            KeyboardButton(text="📜 История"),
            KeyboardButton(text="🔥 Топ-сделки"),
        ],
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
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO!\n\n"
        "Выберите опцию в меню ниже:",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text == "⚙️ Настройки")
async def text_settings(message: types.Message):
    async with AsyncSessionLocal() as session:
        setting = await get_or_create_setting(session, message.from_user.id)
    await message.answer(
        "📊 Текущие настройки:\n"
        f"• Биржа: <b>{setting.exchange}</b>\n"
        f"• Buy ≤ <b>{setting.buy_threshold or '—'}</b>\n"
        f"• Sell ≥ <b>{setting.sell_threshold or '—'}</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text == "🧮 Калькулятор")
async def text_calculator(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите через пробел: сумма buy_price sell_price\n"
        "Например: <code>100 41.20 42.50</code>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CalcStates.waiting_input)

@router.message(StateFilter(CalcStates.waiting_input))
async def calc_input(message: types.Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer(
            "Неверный формат. Введите три числа через пробел, например: 100 41.20 42.50",
            reply_markup=ReplyKeyboardRemove()
        )
    try:
        amount, buy_p, sell_p = map(float, parts)
    except ValueError:
        return await message.answer(
            "Пожалуйста, вводите только числа, например: 100 41.20 42.50",
            reply_markup=ReplyKeyboardRemove()
        )
    profit = amount * (sell_p - buy_p)
    await message.answer(
        f"💰 Прибыль: {amount}×({sell_p}−{buy_p}) = <b>{profit:.2f}₴</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KB
    )
    await state.clear()

@router.message(lambda message: message.text == "📜 История")
async def text_history(message: types.Message):
    await message.answer(
        "🕑 История сделок:\n(пока нет данных)",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text == "🔥 Топ-сделки")
async def text_top(message: types.Message):
    await message.answer(
        "🏆 Топ-сделки за сегодня:\n(пока нет данных)",
        reply_markup=MAIN_KB
    )
