from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# Закреплённая клавиатура
MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/settings"),
            KeyboardButton(text="/start"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# ... (get_setting остаётся без изменений) ...

@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ArbitPRO Bot.\n"
        "В базовой версии я отслеживаю P2P-арбитраж USDT между Binance, Bybit и Bitget.\n"
        "Используй /settings для установки порогов.",
        reply_markup=MAIN_KB
    )

@router.message(Command(commands=["settings"]))
async def cmd_settings(message: types.Message):
    # ... код без изменений, но с reply_markup=MAIN_KB ...
    await message.answer(text, reply_markup=MAIN_KB)
