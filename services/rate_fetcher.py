import aiohttp
from utils.logger import logger

async def fetch_rates() -> dict:
    results = {}

    async with aiohttp.ClientSession() as session:
        # === Binance P2P ===
        try:
            url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
            payload = {"asset": "USDT", "fiat": "USD", "tradeType": "BUY", "rows": 1, "page": 1}
            async with session.post(url, json=payload, timeout=5) as resp:
                data = await resp.json()
                advs = data.get("data", [])
                price = float(advs[0]["adv"]["price"]) if advs else 0.0
                results["binance"] = {"buy": price, "sell": price}
        except Exception as e:
            logger.error(f"Error fetching rates from binance: {e}")
            results["binance"] = {"buy": 0.0, "sell": 0.0}

        # === Bybit P2P ===
        try:
            url = "https://api.bybit.com/p2p/v1/public/ads"
            params = {"symbol": "USDT", "side": "BUY", "currency": "USD", "page": 1, "limit": 1}
            async with session.get(url, params=params, timeout=5) as resp:
                data = await resp.json()
                ads = data.get("result", {}).get("list", [])
                price = float(ads[0]["price"]) if ads else 0.0
                results["bybit"] = {"buy": price, "sell": price}
        except Exception as e:
            logger.error(f"Error fetching rates from bybit: {e}")
            results["bybit"] = {"buy": 0.0, "sell": 0.0}

        # === Bitget P2P ===
        try:
            url = "https://api.bitget.com/api/p2p/v1/public/offers"
            params = {"symbol": "USDT_USD", "type": "BUY", "pageSize": 1, "pageNo": 1}
            async with session.get(url, params=params, timeout=5) as resp:
                data = await resp.json()
                offers = data.get("data", [])
                price = float(offers[0]["price"]) if offers else 0.0
                results["bitget"] = {"buy": price, "sell": price}
        except Exception as e:
            logger.error(f"Error fetching rates from bitget: {e}")
            results["bitget"] = {"buy": 0.0, "sell": 0.0}

    return results
