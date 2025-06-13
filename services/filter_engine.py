import asyncio
from sqlalchemy import select
from aiogram import Bot
from config.db import AsyncSessionLocal
from models.user_setting import UserSetting
from config.config import API_TOKEN

# Инициализируем бот для отправки уведомлений
bot = Bot(token=API_TOKEN)

async def filter_and_notify(rates: dict):
    # Открываем сессию к БД
    async with AsyncSessionLocal() as session:
        # Выполняем запрос, получаем объекты UserSetting
        result = await session.execute(select(UserSetting))
        settings = result.scalars().all()

    # Для каждого объекта-настройки проверяем пороги
    for setting in settings:
        # Убеждаемся, что это действительно модель, а не int
        # (если здесь снова int — файл не заменён корректно)
        exch = setting.exchange
        buy_p = rates.get(exch, {}).get("buy")
        sell_p = rates.get(exch, {}).get("sell")
        tasks = []

        if setting.buy_threshold is not None and buy_p is not None:
            if buy_p <= setting.buy_threshold:
                msg = (
                    f"🟢 Возможность покупки на {exch.title()}!\n"
                    f"Цена: {buy_p}₴ (≤ ваш порог {setting.buy_threshold}₴)\n"
                    "Объём до $100"
                )
                tasks.append(bot.send_message(setting.user_id, msg))

        if setting.sell_threshold is not None and sell_p is not None:
            if sell_p >= setting.sell_threshold:
                msg = (
                    f"🔴 Возможность продажи на {exch.title()}!\n"
                    f"Цена: {sell_p}₴ (≥ ваш порог {setting.sell_threshold}₴)\n"
                    "Объём до $100"
                )
                tasks.append(bot.send_message(setting.user_id, msg))

        if tasks:
            # Отправляем все сообщения параллельно
            asyncio.gather(*tasks)
