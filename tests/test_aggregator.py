import asyncio
import json
import pytest
from unittest.mock import AsyncMock

from services import aggregator
from services.aggregator import start_aggregator


class FakeResp:
    def __init__(self, data):
        self._data = data

    async def json(self):
        return self._data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeSession:
    def __init__(self, data):
        self._data = data

    def get(self, url):
        return FakeResp(self._data)


@pytest.mark.asyncio
async def test_start_aggregator_sends_notification(monkeypatch, tmp_path):
    filters = {"10": {"buy_price": 100, "sell_price": 120, "volume": 10}}
    fpath = tmp_path / "filters.json"
    fpath.write_text(json.dumps(filters))

    api_data = {
        "result": {
            "list": [
                {
                    "symbol": "ABC",
                    "bid1Price": "90",
                    "ask1Price": "130",
                    "bid1Size": "0.1",
                    "lastPrice": "90"
                }
            ]
        }
    }

    session = FakeSession(api_data)
    bot = AsyncMock()

    monkeypatch.setattr(aggregator, "FILTERS_FILE", str(fpath))

    async def fake_sleep(_):
        raise asyncio.CancelledError

    monkeypatch.setattr(aggregator.asyncio, "sleep", fake_sleep)

    with pytest.raises(asyncio.CancelledError):
        await start_aggregator(session, bot)

    bot.send_message.assert_called_once()
    args, _ = bot.send_message.call_args
    assert args[0] == "10"
    assert "ABC" in args[1]
