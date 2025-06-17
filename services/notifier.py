import asyncio
import logging
from aiogram import Bot

async def notifier_worker(queue: asyncio.Queue, bot: Bot):
    while True:
        try:
            alert = await queue.get()
            chat_id = alert.get("chat_id")
            message = alert.get("message")
            if chat_id and message:
                await bot.send_message(chat_id, message, parse_mode="HTML")
                logging.info(f"📤 Отправлено сообщение для {chat_id}")
        except Exception as e:
            logging.error(f"❌ Ошибка в notifier_worker: {e}")
        await asyncio.sleep(0.5)
