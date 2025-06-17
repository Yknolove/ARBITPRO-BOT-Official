import asyncio
import aiohttp
import json
import os
import logging
from services.rate_fetcher import RateFetcher

FILTERS_FILE = "filters.json"

async def start_aggregator(bot):
    logging.info("🟢 Агрегатор запущен")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                rf = RateFetcher(session)
                tickers = await rf.fetch_bybit()
                logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

                if not os.path.exists(FILTERS_FILE):
                    with open(FILTERS_FILE, "w") as f:
                        json.dump({}, f)

                try:
                    with open(FILTERS_FILE, "r") as f:
                        filters = json.load(f)
                except Exception as fe:
                    logging.error("❗ Ошибка загрузки фильтров", exc_info=fe)
                    filters = {}

                for chat_id, fdata in filters.items():
                    try:
                        buy_limit = float(fdata.get("buy_price", 0))
                        sell_limit = float(fdata.get("sell_price", 1000000))
                        vol_limit = float(fdata.get("volume", 1000000))
                    except:
                        continue

                    for t in tickers:
                        try:
                            price = float(t["price"])
                            vol = float(t["volume"])
                            if price <= buy_limit and price >= sell_limit and vol <= vol_limit:
                                msg = (
                                    f"💰 <b>Найдена сделка</b>\n"
                                    f"<b>Тикер:</b> {t['symbol']}\n"
                                    f"<b>Цена:</b> {price}$\n"
                                    f"<b>Объём:</b> {vol}$"
                                )
                                try:
                                    await bot.send_message(chat_id=int(chat_id), text=msg, parse_mode="HTML")
                                except Exception as send_err:
                                    logging.error(f"❌ Ошибка отправки: {send_err}")
                        except:
                            continue

        except Exception as e:
            logging.error("💥 Ошибка в агрегаторе", exc_info=e)

        logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
        await asyncio.sleep(15)
