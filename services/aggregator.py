import asyncio
import json
import logging
from services.rate_fetcher import RateFetcher
from services.filter_engine import apply_filters

FILTERS_FILE = "filters.json"

async def start_aggregator(bot):
    while True:
        try:
            from aiohttp import ClientSession
            async with ClientSession() as session:
                rf = RateFetcher(session)
                tickers = await rf.fetch_bybit()
                logging.info(f"🟢 Получено {len(tickers)} тикеров от Bybit")

                matched = apply_filters(tickers, FILTERS_FILE)

                for item in matched:
                    try:
                        msg = (
                            f"📣 Сделка найдена:\n"
                            f"Пара: {item['symbol']}\n"
                            f"Цена: {item['price']}$\n"
                            f"Объём: {item['volume']}$"
                        )
                        await bot.send_message(chat_id=int(item['chat_id']), text=msg)
                    except Exception as err:
                        logging.error(f"❌ Ошибка отправки: {err}")

        except Exception as e:
            logging.error("💥 Критическая ошибка агрегатора", exc_info=e)

        await asyncio.sleep(15)
