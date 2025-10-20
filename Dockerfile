# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DB_PATH=/app/app.db \
    EVIDENCE_DIR=/app/EVIDENCE/S08

# curl нужен только для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код приложения и тесты
COPY app ./app

# создаём non-root пользователя и отдаём права на /app
RUN useradd -r -u 10001 -g users appuser \
  && chown -R appuser:users /app

USER appuser

EXPOSE 8000

# простой healthcheck
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -fsS http://127.0.0.1:8000/ || exit 1

# просто запускаем uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
