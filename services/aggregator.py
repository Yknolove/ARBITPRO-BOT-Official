import asyncio
from services.rate_fetcher import RateFetcher
import aiohttp

async def start_aggregator(bot):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                rf = RateFetcher(session)
                bybit_data = await rf.fetch_bybit()

                # Здесь может быть логика фильтрации и отправки уведомлений
                # Например:
                # await bot.send_message(chat_id, "Новая сделка...")

        except Exception as e:
            print(f"Aggregator error: {e}")

        await asyncio.sleep(15)
                logging.error(f"Ошибка в обработке фильтра пользователя {chat_id}", exc_info=e)

        await asyncio.sleep(15)
