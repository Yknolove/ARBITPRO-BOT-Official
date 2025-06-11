from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting

router = Router()

async def get_setting(session: AsyncSession, user_id: int):
    setting = await session.get(UserSetting, user_id)
    if not setting:
        setting = UserSetting(user_id=user_id)
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting

@router.message(Command("settings"))
async def cmd_settings(message: types.Message):
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
    text = (
        f"Текущие настройки:\n"
        f"• Биржа: {setting.exchange}\n"
        f"• Buy ≤ {setting.buy_threshold or 'не задан'}\n"
        f"• Sell ≥ {setting.sell_threshold or 'не задан'}\n\n"
        "Установить:\n"
        "/set_exchange <binance|bybit|bitget>\n"
        "/set_buy <цена>\n"
        "/set_sell <цена>"
    )
    await message.answer(text)

@router.message(Command("set_exchange"))
async def cmd_set_exchange(message: types.Message, command: CommandObject):
    exch = command.args.lower()
    if exch not in ("binance", "bybit", "bitget"):
        return await message.answer("Неверная биржа. Выберите: binance, bybit или bitget.")
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.exchange = exch
        await session.commit()
    await message.answer(f"Биржа установлена на {exch}.")

@router.message(Command("set_buy"))
async def cmd_set_buy(message: types.Message, command: CommandObject):
    try:
        val = float(command.args)
    except:
        return await message.answer("Неверный формат цены. Например: /set_buy 41.20")
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.buy_threshold = val
        await session.commit()
    await message.answer(f"Порог покупки установлен: ≤ {val}₴.")

@router.message(Command("set_sell"))
async def cmd_set_sell(message: types.Message, command: CommandObject):
    try:
        val = float(command.args)
    except:
        return await message.answer("Неверный формат цены. Например: /set_sell 42.50")
    async with AsyncSessionLocal() as session:
        setting = await get_setting(session, message.from_user.id)
        setting.sell_threshold = val
        await session.commit()
    await message.answer(f"Порог продажи установлен: ≥ {val}₴.")
