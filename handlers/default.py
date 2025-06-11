from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ArbitPRO Bot.\n"
        "В базовой версии я отслеживаю P2P-арбитраж USDT между Binance, Bybit и Bitget.\n"
        "Используй /settings для установки порогов."
    )

@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    # TODO: показать текущие пороги и кнопки для установки
    await message.answer("Здесь настройка фильтров (купить ≤ X, продать ≥ Y).")
