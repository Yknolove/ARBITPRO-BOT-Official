# services/aggregator.py

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import AsyncSessionLocal
from models.user_setting import UserSetting
from services.filter_engine import filter_and_notify
from services.rate_fetcher import fetch_rates  # Замените на вашу функцию получения курсов
from utils.logger import logger

# Интервал опроса бирж в секундах
POLL_INTERVAL = 10

async def start_aggregator():
    """
    Фоновая задача, которая раз в POLL_INTERVAL секунд:
      1) Получает актуальные курсы с бирж.
      2) Загружает настройки всех пользователей из БД.
      3) Вызывает filter_and_notify(rates, user_settings).
    """
    while True:
        try:
            # Шаг 1: получить курсы
            rates = await fetch_rates()
            logger.info(f"Fetched rates: {rates}")

            # Шаг 2: загрузить все пользовательские настройки
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(UserSetting))
                user_settings = result.scalars().all()

            # Шаг 3: отфильтровать и разослать уведомления
            await filter_and_notify(rates, user_settings)

        except Exception as e:
            logger.error(f"Aggregator error: {e}")

        # Подождать перед следующим опросом
        await asyncio.sleep(POLL_INTERVAL)
