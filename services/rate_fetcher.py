import aiohttp

class RateFetcher:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_bybit(self):
        url = "https://api.bybit.com/v5/market/tickers?category=spot"  # 📌 исправленный эндпойнт

        async with self.session.get(url) as resp:
            if resp.content_type != "application/json":
                text = await resp.text()
                raise Exception(f"❌ Не JSON ответ: {resp.content_type}, текст: {text}")

            data = await resp.json()
            # Извлекаем нужный массив тикеров
            tickers = data.get("result", {}).get("list", [])
            filtered = []
            for item in tickers:
                try:
                    symbol = item.get("symbol", "")
                    price = float(item.get("lastPrice", 0))
                    volume = float(item.get("turnover24h", 0))
                    filtered.append({"symbol": symbol, "price": price, "volume": volume})
                except:
                    continue
            return filtered
