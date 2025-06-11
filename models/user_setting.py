import aiohttp

async def keep_awake():
    """Регулярно пингует собственный /ping, чтобы инстанс не засыпал."""
    # Дадим время на инициализацию бота
    await asyncio.sleep(5)
    url = WEBHOOK_URL + "/ping"
    session = aiohttp.ClientSession()
    try:
        while True:
            try:
                await session.get(url)
            except Exception:
                pass
            # Пинг каждые 30 секунд
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        # При отмене таска корректно закрываем сессию
        await session.close()
        raise

# Внутри on_startup() добавляем после старта агрегатора:
async def on_startup():
    await init_db()
    await set_commands()
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    asyncio.create_task(start_aggregator(filter_and_notify))
    # Запускаем keep_awake
    asyncio.create_task(keep_awake())
