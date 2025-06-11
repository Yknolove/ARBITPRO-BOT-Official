import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from config.db import AsyncSessionLocal
from models.user_setting import UserSetting
from config.config import API_TOKEN

bot = Bot(token=API_TOKEN)  # без parse_mode, нам тут только send_message

async def filter_and_notify(rates: dict):
    async with AsyncSessionLocal() as session:
        # получаем все настройки
        result = await session.execute(
            UserSetting.__table__.select()
        )
        settings = result.scalars().all()

    for setting in settings:
        exch = setting.exchange
        buy_p = rates[exch]["buy"]
        sell_p = rates[exch]["sell"]

        tasks = []
        if setting.buy_threshold is not None and buy_p <= setting.buy_threshold:
            text = (
                f"🟢 Возможность покупки на {exch.title()}!\n"
                f"Цена: {buy_p}₴ (≤ ваш порог {setting.buy_threshold}₴)\n"
                f"Объём до $100"
            )
            tasks.append(bot.send_message(setting.user_id, text))

        if setting.sell_threshold is not None and sell_p >= setting.sell_threshold:
            text = (
                f"🔴 Возможность продажи на {exch.title()}!\n"
                f"Цена: {sell_p}₴ (≥ ваш порог {setting.sell_threshold}₴)\n"
                f"Объём до $100"
            )
            tasks.append(bot.send_message(setting.user_id, text))

        if tasks:
            # запускаем все отправки, не дожидаясь, чтобы не блокировать остальных
            asyncio.gather(*tasks)
