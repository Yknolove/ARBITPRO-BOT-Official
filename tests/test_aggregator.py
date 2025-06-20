import asyncio
import json
import pytest
from unittest.mock import AsyncMock

from services import aggregator
from services.aggregator import start_aggregator


@pytest.mark.asyncio
async def test_start_aggregator_sends_notification(monkeypatch, tmp_path):
    filters = {"10": {"buy_price": 100, "sell_price": 120, "volume": 10}}
    fpath = tmp_path / "filters.json"
    fpath.write_text(json.dumps(filters))

    bot = AsyncMock()

    monkeypatch.setattr(aggregator, "FILTERS_FILE", str(fpath))

    async def fake_fetch(_session):
        return [
            {
                "symbol": "ABC",
                "price": 90,
                "sell_price": 130,
                "buy": 90,
                "sell": 130,
                "volume": 0.1,
            }
        ]

    async def fake_sleep(_):
        raise asyncio.CancelledError

    monkeypatch.setattr(aggregator, "fetch_p2p_orders", fake_fetch)
    monkeypatch.setattr(aggregator.asyncio, "sleep", fake_sleep)

    with pytest.raises(asyncio.CancelledError):
        await start_aggregator(None, bot)

    bot.send_message.assert_called_once()
    args, _ = bot.send_message.call_args
    assert args[0] == "10"
    assert "ABC" in args[1]


@pytest.mark.asyncio
async def test_start_aggregator_multiple_chat_ids(monkeypatch, tmp_path):
    filters = {
        "10": {"buy_price": 100, "sell_price": 120, "volume": 10},
        "20": {"buy_price": 100, "sell_price": 120, "volume": 10},
    }
    fpath = tmp_path / "filters.json"
    fpath.write_text(json.dumps(filters))

    bot = AsyncMock()

    monkeypatch.setattr(aggregator, "FILTERS_FILE", str(fpath))

    async def fake_fetch(_session):
        return [
            {
                "symbol": "XYZ",
                "price": 90,
                "sell_price": 125,
                "buy": 90,
                "sell": 125,
                "volume": 0.05,
            }
        ]

    async def fake_sleep(_):
        raise asyncio.CancelledError

    monkeypatch.setattr(aggregator, "fetch_p2p_orders", fake_fetch)
    monkeypatch.setattr(aggregator.asyncio, "sleep", fake_sleep)

    with pytest.raises(asyncio.CancelledError):
        await start_aggregator(None, bot)

    assert bot.send_message.call_count == 2
    called_ids = {call.args[0] for call in bot.send_message.call_args_list}
    assert called_ids == {"10", "20"}
