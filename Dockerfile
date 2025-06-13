# ───────────────────────────────────────────────────────
# 1) Базовый образ Python
FROM python:3.11-slim

# 2) Рабочая директория внутри контейнера
WORKDIR /app

# 3) Копируем файл зависимостей
COPY requirements.txt .

# 4) Создаём виртуальное окружение и ставим зависимости
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r requirements.txt

# 5) Копируем весь код проекта
COPY . .

# 6) Устанавливаем PATH, чтобы python и pip из venv работали по умолчанию
ENV PATH="/opt/venv/bin:$PATH"

# 7) Команда запуска бота
CMD ["python", "main.py"]
# ───────────────────────────────────────────────────────
