# Указываем базовый образ с Python
FROM python:3.11-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Создаём venv и ставим зависимости
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r requirements.txt

# Копируем весь код
COPY . .

# Указываем команду запуска
CMD ["/opt/venv/bin/python", "main.py"]
