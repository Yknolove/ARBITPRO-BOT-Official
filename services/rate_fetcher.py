# services/rate_fetcher.py

import aiohttp
from bs4 import BeautifulSoup
from utils.logger import logger

async def fetch_bybit_p2p_price(session: aiohttp.ClientSession) -> float:
    """
    Скрейпинг первой цены P2P Bybit с публичной страницы.
    """
    url = "https://www.bybit.com/ru/peer-to-peer/USDT_USD"
    async with session.get(url, timeout=10) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, "html.parser")
    price_elem = soup.select_one(".p2p-booking-card__price")
    if not price_elem:
        raise ValueError("Не удалось найти цену на Bybit P2P")
    price_str = price_elem.get_text(strip=True).split()[0]
    return float(price_str.replace(",", ""))

async def fetch_bitget_p2p_price(session: aiohttp.ClientSession) -> float:
    """
    Скрейпинг первой цены P2P Bitget с публичной страницы.
    """
    url = "https://www.bitget.com/ru/p2p/USDT_USD"
    async with session.get(url, timeout=10) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, "html.parser")
    price_elem = soup.select_one(".p2p-deal-card-price")
    if not price_elem:
        raise ValueError("Не удалось найти цену на Bitget P2P")
    price_str = price_elem.get_text(strip=True).split()[0]
    return float(price_str.replace(",", ""))

async def fetch_binance_p2p_price(session: aiohttp.ClientSession) -> float:
    """
    Получение первой цены P2P Binance через публичный JSON API.
    """
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "USD",
        "tradeType": "BUY",
        "rows": 1,
        "page": 1
    }
    async with session.post(url, json=payload, timeout=5) as resp:
        data = await resp.json()
    advs = data.get("data", [])
    if not advs:
        return 0.0
    return float(advs[0]["adv"]["price"])

async def fetch_rates() -> dict:
    """
    Возвращает текущие P2P-курсы USDT для Binance, Bybit и Bitget:
      {
        "binance": {"buy": float, "sell": float},
        "bybit":   {"buy": float, "sell": float},
        "bitget":  {"buy": float, "sell": float},
      }
    """
    results = {}
    async with aiohttp.ClientSession() as session:
        # Binance
        try:
            price = await fetch_binance_p2p_price(session)
            results["binance"] = {"buy": price, "sell": price}
        except Exception as e:
            logger.error(f"Binance P2P error: {e}")
            results["binance"] = {"buy": 0.0, "sell": 0.0}

        # Bybit
        try:
            price = await fetch_bybit_p2p_price(session)
            results["bybit"] = {"buy": price, "sell": price}
        except Exception as e:
            logger.error(f"Bybit P2P scrape error: {e}")
            results["bybit"] = {"buy": 0.0, "sell": 0.0}

        # Bitget
        try:
            price = await fetch_bitget_p2p_price(session)
            results["bitget"] = {"buy": price, "sell": price}
        except Exception as e:
            logger.error(f"Bitget P2P scrape error: {e}")
            results["bitget"] = {"buy": 0.0, "sell": 0.0}

    return results
