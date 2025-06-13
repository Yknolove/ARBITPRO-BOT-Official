FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install -r requirements.txt
COPY . .
ENV PATH="/opt/venv/bin:$PATH"
CMD ["python", "main.py"]
# ───────────────────────────────────────────────────────
