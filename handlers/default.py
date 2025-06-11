from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

# готовим постоянную клавиатуру внизу
MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("/settings"), KeyboardButton("/start")],
    ],
    resize_keyboard=True
)

async def get_setting(session: AsyncSession, user_id: int):
    setting = await session.get(UserSetting, user_id)
    if not setting:
        setting = UserSetting(user_id=user_id)
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ArbitPRO Bot.\n"
        "В базовой версии я отслеживаю P2P-арбитраж USDT между Binance, Bybit и Bitget.\n"
        "Используй /settings для установки порогов.",
        reply_markup=MAIN_KB
    )

@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)

    text = (
        "Текущие настройки:\n"
        f"• Биржа: <b>{setting.exchange}</b>\n"
        f"• Buy ≤ <b>{setting.buy_threshold or 'не задан'}</b>\n"
        f"• Sell ≥ <b>{setting.sell_threshold or 'не задан'}</b>\n\n"
        "Установить:\n"
        "<code>/set_exchange binance</code> — выбрать биржу\n"
        "<code>/set_buy 41.20</code> — задать порог покупки\n"
        "<code>/set_sell 42.50</code> — задать порог продажи"
    )
    await message.answer(text, reply_markup=MAIN_KB)

@router.message(Command("set_exchange"))
async def cmd_set_exchange(message: types.Message, command: CommandObject):
    exch = command.args.lower()
    if exch not in ("binance", "bybit", "bitget"):
        return await message.answer(
            "Неверная биржа. Выберите: binance, bybit или bitget.",
            reply_markup=MAIN_KB
        )
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.exchange = exch
        await session.commit()
    await message.answer(f"Биржа установлена на <b>{exch}</b>.", reply_markup=MAIN_KB)

@router.message(Command("set_buy"))
async def cmd_set_buy(message: types.Message, command: CommandObject):
    try:
        val = float(command.args)
    except ValueError:
        return await message.answer(
            "Неверный формат цены. Например: /set_buy 41.20",
            reply_markup=MAIN_KB
        )
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.buy_threshold = val
        await session.commit()
    await message.answer(f"Порог покупки установлен: ≤ <b>{val}₴</b>.", reply_markup=MAIN_KB)

@router.message(Command("set_sell"))
async def cmd_set_sell(message: types.Message, command: CommandObject):
    try:
        val = float(command.args)
    except ValueError:
        return await message.answer(
            "Неверный формат цены. Например: /set_sell 42.50",
            reply_markup=MAIN_KB
        )
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.sell_threshold = val
        await session.commit()
    await message.answer(f"Порог продажи установлен: ≥ <b>{val}₴</b>.", reply_markup=MAIN_KB)
