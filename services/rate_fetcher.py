import aiohttp

class RateFetcher:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_bybit(self):
        url = "https://api.bybit.com/v2/public/tickers?symbol=USDTUSD"
        async with self.session.get(url) as r:
            if r.status != 200:
                text = await r.text()
                print("❌ Ошибка Bybit:", r.status, text)
                return {}

            try:
                d = await r.json()
                return {"order": {
                    "price": float(d["result"][0]["last_price"]),
                    "volume": 100,  # 💡 Заглушка, если объёма нет
                    "link": "https://www.bybit.com/en-US/trade/spot/USDT/USD"
                }}
            except Exception as e:
                print("❌ Ошибка обработки JSON от Bybit:", e)
                return {}
