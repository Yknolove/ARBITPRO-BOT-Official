FROM python:3.11-slim

WORKDIR /app

# 1) Копируем зависимости и устанавливаем их в venv
COPY requirements.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
 && /opt/venv/bin/pip install -r requirements.txt

# 2) Копируем всё остальное
COPY . .

# 3) Делаем venv-энвайрон доступным
ENV PATH="/opt/venv/bin:$PATH"

# 4) Запуск основного скрипта
CMD ["python", "main.py"]
