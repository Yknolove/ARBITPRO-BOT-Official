# services/filter_engine.py

import asyncio
from services.notifier import notify_user

async def filter_and_notify(rates: dict, user_settings: list) -> None:
    """
    Проходит по списку пользовательских настроек, проверяет условия
    и при необходимости отправляет уведомления.
    :param rates: текущие курсы {exchange: {buy: ..., sell: ...}, ...}
    :param user_settings: список объектов UserSetting
    """
    tasks = []
    for st in user_settings:
        # Пример логики: если на выбранной бирже текущий SELL >= threshold
        current = rates.get(st.exchange, {})
        if current.get("sell", 0) >= (st.sell_threshold or 0):
            text = (
                f"🔔 Арбитражное условие достигнуто!\n"
                f"<b>Биржа:</b> {st.exchange}\n"
                f"<b>SELL:</b> {current['sell']}\n"
                f"Ваш порог: ≥ {st.sell_threshold}"
            )
            tasks.append(notify_user(st.user_id, text))
        # Аналогично можно добавить проверку BUY и объёма...
    if tasks:
        # Ждём отправки всех уведомлений
        await asyncio.gather(*tasks)
