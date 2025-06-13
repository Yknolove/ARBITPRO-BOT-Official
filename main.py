import os
import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Необязательно: если хотите хранить токен в файле .env,
# раскомментируйте и установите python-dotenv (pip install python-dotenv):
# from dotenv import load_dotenv
# load_dotenv()  # загрузит переменные из .env в корне проекта

# Получаем токен
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❗ Переменная окружения API_TOKEN не установлена")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


@dp.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer(f"👋 Привет! Ты написал: {message.text}")


async def main() -> None:
    logging.info("🚀 Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен.")
