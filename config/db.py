# config/db.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Импортируем DATABASE_URL из config.config как DB_URL
from config.config import DATABASE_URL as DB_URL

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(
    DB_URL,
    echo=False,            # Отключаем вывод SQL-запросов в лог (можно True для отладки)
)

# Фабрика сессий для асинхронных операций
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # После коммита объекты не будут "просрочены"
)

# Базовый класс для декларативного описания моделей
Base = declarative_base()
