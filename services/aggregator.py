import asyncio
import aiohttp
from services.rate_fetcher import RateFetcher
import logging

async def start_aggregator(bot):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                rf = RateFetcher(session)
                tickers = await rf.fetch_bybit()
                print(f"✅ Загружено {len(tickers)} тикеров с Bybit")

        except Exception as e:
            logging.error("❌ Ошибка в агрегаторе", exc_info=e)

        await asyncio.sleep(15)
