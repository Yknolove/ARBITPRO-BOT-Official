from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.filters.state import StateFilter
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
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO!

"
        "Выберите опцию в меню ниже:",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text and "настройк" in message.text.lower())
async def text_settings(message: types.Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        setting = await get_or_create_setting(session, message.from_user.id)
    await message.answer(
        "📊 Текущие настройки:
"
        f"• Биржа: <b>{setting.exchange}</b>
"
        f"• Buy ≤ <b>{setting.buy_threshold or '—'}</b>
"
        f"• Sell ≥ <b>{setting.sell_threshold or '—'}</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text and ("калькулятор" in message.text.lower() or "🧮" in message.text))
async def text_calculator(message: types.Message, state: FSMContext):
    # Открываем диалог для ввода
    await message.answer(
        "Введите через пробел: сумма buy_price sell_price
"
        "Например: <code>100 41.20 42.50</code>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CalcStates.waiting_input)

@router.message(StateFilter(CalcStates.waiting_input))
async def calc_input(message: types.Message, state: FSMContext):
    # Обработка ввода калькулятора
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer(
            "Неверный формат. Введите три числа через пробел, например: 100 41.20 42.50",
            reply_markup=MAIN_KB
        )
    try:
        amount, buy_p, sell_p = map(float, parts)
    except ValueError:
        return await message.answer(
            "Пожалуйста, вводите только числа, например: 100 41.20 42.50",
            reply_markup=MAIN_KB
        )
    profit = amount * (sell_p - buy_p)
    await state.clear()
    await message.answer(
        f"💰 Прибыль: {amount}×({sell_p}−{buy_p}) = <b>{profit:.2f}₴</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text and "история" in message.text.lower())
async def text_history(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🕑 История сделок:
(пока нет данных)",
        reply_markup=MAIN_KB
    )

@router.message(lambda message: message.text and ("топ" in message.text.lower() or "🔥" in message.text))
async def text_top(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏆 Топ-сделки за сегодня:
(пока нет данных)",
        reply_markup=MAIN_KB
    )
