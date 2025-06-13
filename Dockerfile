FROM python:3.11-slim

WORKDIR /app

# Копируем только файл с зависимостями
COPY requirements.txt .

# Создаём виртуальное окружение и ставим зависимости
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
 && /opt/venv/bin/pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Делаем /opt/venv/bin доступным
ENV PATH="/opt/venv/bin:$PATH"

# При запуске контейнера — стартуем бота
CMD ["python", "main.py"]
