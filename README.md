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

3. **Configure environment variables** (or create a `.env` file):

- `API_TOKEN` – Telegram bot token
- `WEBHOOK_URL` – public HTTPS URL for Telegram webhooks (`https://<your-host>/webhook`)
- `PORT` – port to run the web server (default: `10000`)

Example `.env`:

```env
API_TOKEN=<your-token>
WEBHOOK_URL=https://example.com/webhook
PORT=10000
```

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

