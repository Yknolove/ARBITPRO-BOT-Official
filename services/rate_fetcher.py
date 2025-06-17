class RateFetcher:
    def __init__(self, session):
        self.session = session

    async def fetch_bybit(self):
        url = "url = "https://api.bybit.com/v5/market/tickers?category=spot"  # ← убран ;
        async with self.session.get(url) as resp:
            if resp.content_type != "application/json":
                text = await resp.text()
                raise Exception(f"❌ Не JSON ответ: {resp.content_type}, текст: {text}")

            data = await resp.json()
            filtered = []
            for item in data.get("result", []):
                try:
                    symbol = item.get("symbol", "")
                    price = float(item.get("last_price", 0))
                    volume = float(item.get("turnover_24h", 0))
                    filtered.append({"symbol": symbol, "price": price, "volume": volume})
                except:
                    continue
            return filtered
