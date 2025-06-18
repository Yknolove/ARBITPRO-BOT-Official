def apply_filters(tickers, filters_file):
    import logging
    try:
        with open(filters_file, "r") as f:
            filters = json.load(f)
    except Exception:
        filters = {}

    results = []
    for chat_id, f in filters.items():
        buy_limit = float(f.get("buy_price", 0))
        sell_limit = float(f.get("sell_price", 999999))
        vol_limit = float(f.get("volume", 100))
        exchange = f.get("exchange", "bybit")

        for t in tickers:
            # Debug print
            if "price" not in t:
                logging.warning(f"[filter_engine] Нет ключа 'price' в: {t}")
                continue
            if (
                t["price"] <= buy_limit and
                t.get("sell_price", t["price"]) >= sell_limit and
                t.get("volume", 0) <= vol_limit
            ):
                results.append({
                    **t,
                    "chat_id": chat_id,
                    "exchange": exchange
                })
    return results
