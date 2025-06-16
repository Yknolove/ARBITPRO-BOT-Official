from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json

router = Router()

FILTERS_FILE = "filters.json"

@router.callback_query(F.data == "arbitrage")
async def show_arbitrage(call: CallbackQuery):
    user_id = str(call.from_user.id)
    try:
        with open(FILTERS_FILE, "r") as f:
            filters = json.load(f)
        user_filter = filters.get(user_id)
    except:
        user_filter = None

    if not user_filter:
        await call.message.edit_text(
            "📊 <b>Арбитраж</b>

"
            "❗ У вас не настроен фильтр.
"
            "Используйте команду /filter, чтобы его создать.",
            parse_mode="HTML"
        )
        return

    # Здесь будут загружены данные из агрегатора
    # Для примера, мы покажем заглушку
    example_deals = [
        {"buy": 41.10, "sell": 42.85, "volume": 95, "url": "https://example.com/deal1"},
        {"buy": 40.90, "sell": 43.00, "volume": 100, "url": "https://example.com/deal2"}
    ]

    matched = []
    for deal in example_deals:
        if (
            deal["buy"] <= user_filter["buy_price"] and
            deal["sell"] >= user_filter["sell_price"] and
            deal["volume"] <= user_filter["volume"]
        ):
            matched.append(deal)

    if not matched:
        await call.message.edit_text(
            "📊 <b>Арбитраж</b>

"
            "⚠️ Сейчас нет подходящих сделок по вашему фильтру.",
            parse_mode="HTML"
        )
        return

    text = "📊 <b>Найдено сделок:</b>

"
    for deal in matched:
        text += (
            f"🟢 Купить по: <b>{deal['buy']}</b>
"
            f"🔴 Продать по: <b>{deal['sell']}</b>
"
            f"💵 Объём: ${deal['volume']}
"
            f"🔗 <a href='{deal['url']}'>Открыть ордер</a>

"
        )

    await call.message.edit_text(text, parse_mode="HTML")
