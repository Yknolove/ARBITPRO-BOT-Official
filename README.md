# ArbitPro Telegram Bot

ArbitPro is a Telegram bot that monitors Bybit spot tickers and sends users notifications when their custom filters for arbitrage opportunities are met. Users can configure price and volume thresholds and receive alerts directly via Telegram.

## Setup

1. **Clone the repository** and create a virtual environment (optional):

```bash
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure environment variables** by copying `.env.example` to `.env` and
   filling in your real values:

```bash
cp .env.example .env
```

Environment variables in `.env`:

- `API_TOKEN` – Telegram bot token
- `WEBHOOK_URL` – public HTTPS URL for Telegram webhooks
- `PORT` – port to run the web server (default: `10000`)

4. **Run the bot**:

```bash
python main.py
```

The bot will start the aggregator and listen for Telegram updates on the specified webhook.

## Running Tests

Execute the test suite with:

```bash
PYTHONPATH=. pytest -q
```

