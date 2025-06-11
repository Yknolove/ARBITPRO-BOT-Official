import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from config.db import AsyncSessionLocal
from models.user_setting import UserSetting
from config.config import API_TOKEN

# Инициализируем бота без parse_mode (только для отправки уведомлений)
bot = Bot(token=API_TOKEN)

async def filter_and_notify(rates: dict):
    # Открываем сессию для работы с БД
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        # Получаем все записи UserSetting
        result = await session.execute(
            select(UserSetting)
        )
        settings = result.scalars().all()

    # Проходим по каждой настройке пользователя
    for setting in settings:
        exch = setting.exchange
        buy_p = rates.get(exch, {}).get("buy")
        sell_p = rates.get(exch, {}).get("sell")
        tasks = []

        # Проверяем порог покупки
        if setting.buy_threshold is not None and buy_p is not None:
            if buy_p <= setting.buy_threshold:
                text = (
                    f"🟢 Возможность покупки на {exch.title()}!\n"
                    f"Цена: {buy_p}₴ (≤ ваш порог {setting.buy_threshold}₴)\n"
                    "Объём до $100"
                )
                tasks.append(bot.send_message(setting.user_id, text))

        # Проверяем порог продажи
        if setting.sell_threshold is not None and sell_p is not None:
            if sell_p >= setting.sell_threshold:
                text = (
                    f"🔴 Возможность продажи на {exch.title()}!\n"
                    f"Цена: {sell_p}₴ (≥ ваш порог {setting.sell_threshold}₴)\n"
                    "Объём до $100"
                )
                tasks.append(bot.send_message(setting.user_id, text))

        # Отправляем уведомления (не дожидаясь их завершения)
        if tasks:
            asyncio.gather(*tasks)
