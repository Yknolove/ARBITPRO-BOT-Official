import logging
import asyncio
from aiohttp import ClientSession
from config import FILTERS_FILE
from services.filter_engine import apply_filters


def parse_tickers(raw):
    """Convert raw API ticker data into normalized dictionaries."""
    tickers = []
    for item in raw:
        try:
            symbol = item.get("symbol", "")
            buy = float(item.get("bid1Price", item.get("lastPrice", 0)))
            sell = float(item.get("ask1Price", item.get("lastPrice", 0)))

            bid_price = float(item.get("bid1Price", 0))
            bid_size = float(item.get("bid1Size", 0))
            if bid_price and bid_size:
                volume = bid_price * bid_size
            else:
                volume = float(item.get("volume24h", 0))

            price = float(item.get("lastPrice", 0))

            tickers.append({
                "symbol": symbol,
                "buy": buy,
                "sell": sell,
                "volume": volume,
                "price": price,
                "sell_price": sell,
            })
        except Exception:
            continue
    return tickers


async def start_aggregator(session: ClientSession, bot):
    logging.info("🟢 Агрегатор запущен")

    while True:
        try:
            async with session.get("https://api.bybit.com/v5/market/tickers?category=spot") as resp:
                data = await resp.json()
                raw = data.get("result", {}).get("list", [])
                tickers = parse_tickers(raw)
                logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

        except Exception as e:
            logging.error("💥 Ошибка при получении данных с Bybit", exc_info=e)
            await asyncio.sleep(15)
            continue

        orders = apply_filters(tickers, FILTERS_FILE)

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
