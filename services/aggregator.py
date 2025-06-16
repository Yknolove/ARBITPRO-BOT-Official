import asyncio
from services.rate_fetcher import RateFetcher
import aiohttp
import logging

async def start_aggregator(bot):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                rf = RateFetcher(session)
                bybit_data = await rf.fetch_bybit()

                # Пример: логика уведомлений
                # await bot.send_message(chat_id, "Новая сделка!")

        except Exception as e:
            logging.error("Ошибка в агрегаторе", exc_info=e)

        await asyncio.sleep(15)
