import asyncio
from services.notifier import notify_user

async def filter_and_notify(rates, user_settings):
    tasks = []
    for st in user_settings:
        # ... ваша логика фильтрации ...
        tasks.append(notify_user(st.user_id, ...))
    # важно: дождаться выполнения всех уведомлений
    await asyncio.gather(*tasks)
