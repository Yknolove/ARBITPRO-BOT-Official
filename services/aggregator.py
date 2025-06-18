import json
import logging
import asyncio
from aiohttp import ClientSession
from config import FILTERS_FILE
from services.filter_engine import apply_filters


async def start_aggregator(queue, session: ClientSession, bot):
    logging.info("🟢 Агрегатор запущен")

    while True:
        try:
            async with session.get("https://api.bybit.com/v5/market/tickers?category=spot") as resp:
                data = await resp.json()
                tickers = data.get("result", {}).get("list", [])
                logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

        except Exception as e:
            logging.error("💥 Ошибка при получении данных с Bybit", exc_info=e)
            await asyncio.sleep(15)
            continue

        try:
            with open(FILTERS_FILE, "r") as f:
                filters = json.load(f)
        except Exception as e:
            logging.warning("❗ Не удалось загрузить фильтры", exc_info=e)
            filters = {}

        orders = apply_filters(tickers, filters)

        for order in orders:
            chat_id = order["chat_id"]
            symbol = order["symbol"]
            buy = order["buy"]
            sell = order["sell"]
            volume = order["volume"]

            text = (
                f"📢 Найден арбитраж по <b>{symbol}</b>:\n"
                f"💰 Покупка: {buy}\n"
                f"💵 Продажа: {sell}\n"
                f"📦 Объём: {volume}"
            )

            try:
                await bot.send_message(chat_id, text, parse_mode="HTML")
            except Exception as e:
                logging.error(f"❌ Не удалось отправить сообщение пользователю {chat_id}", exc_info=e)

        logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
        await asyncio.sleep(15)
