import logging
import asyncio
from aiohttp import ClientSession
from config import FILTERS_FILE
from services.filter_engine import apply_filters
from services.p2p_fetcher import P2PFetcher


async def fetch_p2p_orders(session: ClientSession):
    """Fetch buy/sell orders from supported P2P exchanges."""
    fetcher = P2PFetcher(session)
    return await fetcher.fetch_orders()


async def start_aggregator(session: ClientSession, bot):
    logging.info("🟢 Агрегатор запущен")

    while True:
        try:
            tickers = await fetch_p2p_orders(session)
            logging.info(f"🟢 P2P вернул {len(tickers)} ордеров")
        except Exception as e:
            logging.error("💥 Ошибка при получении данных P2P", exc_info=e)
            await asyncio.sleep(15)
            continue

        orders = apply_filters(tickers, FILTERS_FILE)

        for order in orders:
            chat_id = order["chat_id"]
            symbol = order["symbol"]
            buy = order["buy"]
            sell = order["sell"]
            volume = order["volume"]
            url = order.get("url")

            text = (
                f"📢 Найден арбитраж по <b>{symbol}</b>:\n"
                f"💰 Покупка: {buy}\n"
                f"💵 Продажа: {sell}\n"
                f"📦 Объём: {volume}"
                + (f"\n🔗 <a href='{url}'>Открыть ордер</a>" if url else "")
            )

            try:
                await bot.send_message(chat_id, text, parse_mode="HTML")
            except Exception as e:
                logging.error(f"❌ Не удалось отправить сообщение пользователю {chat_id}", exc_info=e)

        logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
        await asyncio.sleep(15)
