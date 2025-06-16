import asyncio
import logging
import json
from datetime import datetime
from aiogram import Bot
from services.rate_fetcher import RateFetcher

FILTERS_FILE = "filters.json"
HISTORY_FILE = "history.json"

async def start_aggregator(bot: Bot):
    logging.basicConfig(level=logging.INFO)
    rf = RateFetcher()

    while True:
        try:
            bybit_data = await rf.fetch_bybit()
        except Exception as e:
            logging.error("Aggregator error", exc_info=e)
            await asyncio.sleep(10)
            continue

        try:
            with open(FILTERS_FILE, "r") as f:
                filters = json.load(f)
        except:
            filters = {}

        for chat_id, fdata in filters.items():
            if fdata.get("exchange") != "bybit":
                continue

            try:
                if (
                    bybit_data["buy"] <= fdata["buy_price"]
                    and bybit_data["sell"] >= fdata["sell_price"]
                    and bybit_data["volume"] <= fdata["volume"]
                ):
                    profit = (bybit_data["sell"] - bybit_data["buy"]) * bybit_data["volume"]

                    # Отправка уведомления
                    text = (
                        f"📢 <b>Арбитраж найдён!</b>\n\n"
                        f"Биржа: Bybit\n"
                        f"Курс покупки: {bybit_data['buy']}\n"
                        f"Курс продажи: {bybit_data['sell']}\n"
                        f"Объём: {bybit_data['volume']}$\n"
                        f"💰 Прибыль: {profit:.2f} ₴\n\n"
                        f"<a href='https://www.bybit.com'>Перейти к ордеру</a>"
                    )
                    await bot.send_message(chat_id, text, parse_mode="HTML")

                    # Логирование в историю
                    history_record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "exchange": "bybit",
                        "buy": bybit_data["buy"],
                        "sell": bybit_data["sell"],
                        "volume": bybit_data["volume"],
                        "profit": round(profit, 2)
                    }

                    try:
                        with open(HISTORY_FILE, "r") as f:
                            history = json.load(f)
                    except:
                        history = {}

                    if chat_id not in history:
                        history[chat_id] = []

                    history[chat_id].append(history_record)
                    with open(HISTORY_FILE, "w") as f:
                        json.dump(history, f, indent=2)

            except Exception as e:
                logging.error(f"Ошибка в обработке фильтра пользователя {chat_id}", exc_info=e)

        await asyncio.sleep(15)
