import asyncio
import aiohttp
import json
import logging
from aiogram import Bot
from services.rate_fetcher import RateFetcher

FILTERS_PATH = "filters.json"

async def start_aggregator(bot: Bot):
    session = aiohttp.ClientSession()
    rf = RateFetcher(session)

    while True:
        try:
            try:
                with open(FILTERS_PATH, "r") as f:
                    filters = json.load(f)
            except FileNotFoundError:
                filters = {}

            bybit_data = await rf.fetch_bybit()

            for uid, fdata in filters.items():
                try:
                    chat_id = int(fdata["chat_id"])
                    buy_price = fdata["buy_price"]
                    sell_price = fdata["sell_price"]
                    max_volume = fdata["volume"]

                    order = bybit_data.get("order")
                    if not order:
                        continue

                    price = float(order.get("price", 0))
                    volume = float(order.get("volume", 0))

                    if price <= buy_price and price >= sell_price and volume <= max_volume:
                        link = order.get("link", "https://bybit.com/")
                        msg = (
                            "📢 Найден ордер на Bybit!\n\n"
                            f"Цена: {price}\n"
                            f"Объём: ${volume}\n\n"
                            f"🔗 [Перейти к ордеру]({link})"
                        )
                        await bot.send_message(chat_id, msg, parse_mode="Markdown")
                except Exception as user_err:
                    logging.exception(f"Ошибка фильтра для {uid}: {user_err}")

        except Exception:
            logging.exception("Aggregator error")

        await asyncio.sleep(60)
