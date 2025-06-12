# services/rate_fetcher.py

import aiohttp
from utils.logger import logger

async def fetch_rates() -> dict:
    """
    Получает актуальные P2P-курсы USDT с бирж Binance, Bybit и Bitget.
    Возвращает словарь вида:
      {
        "binance": {"buy": float, "sell": float},
        "bybit":   {"buy": float, "sell": float},
        "bitget":  {"buy": float, "sell": float},
      }
    """
    urls = {
        "binance": "https://api.binance.com/api/v3/ticker/bookTicker?symbol=USDTUSDT",
        "bybit":   "https://api.bybit.com/v2/public/tickers?symbol=USDTUSDT",
        "bitget":  "https://api.bitget.com/api/mix/v1/market/depth?symbol=USDTUSDT&limit=5",
    }

    results = {}
    async with aiohttp.ClientSession() as session:
        for exch, url in urls.items():
            try:
                async with session.get(url, timeout=5) as resp:
                    data = await resp.json()
                    # Пример парсинга: подставьте нужные поля из API
                    # Здесь предполагаем, что API возвращают 'bidPrice' и 'askPrice'
                    buy = float(data.get("bidPrice", data.get("data", [{}])[0].get("bid_price", 0)))
                    sell = float(data.get("askPrice", data.get("data", [{}])[0].get("ask_price", 0)))
                    results[exch] = {"buy": buy, "sell": sell}
            except Exception as e:
                logger.error(f"Error fetching rates from {exch}: {e}")
                results[exch] = {"buy": 0.0, "sell": 0.0}

    return results
