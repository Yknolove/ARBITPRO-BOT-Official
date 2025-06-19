import json

def apply_filters(tickers, filters_file):
    try:
        with open(filters_file, "r") as f:
            filters = json.load(f)
    except Exception:
        filters = {}

    results = []
    for chat_id, f in filters.items():
        buy_limit = float(f.get("buy_price", 0))
        sell_limit = float(f.get("sell_price", 999999))
        # "volume" represents the trade size metric used by the aggregator
        # (best bid size or 24h volume). Compare user limit to this value.
        vol_limit = float(f.get("volume", 100))
        exchange = f.get("exchange", "bybit")

        for t in tickers:
            # Исправленная логика фильтрации
            if (
                t["price"] <= buy_limit and
                t.get("sell_price", t["price"]) >= sell_limit and
                t["volume"] <= vol_limit
            ):
                results.append({
                    **t,
                    "chat_id": chat_id,
                    "exchange": exchange
                })
    return results
