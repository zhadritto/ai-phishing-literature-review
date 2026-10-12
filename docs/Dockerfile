FROM python:3.11.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY config.json ./
COPY src/ ./src/
COPY data/sample/ ./data/sample/

CMD ["python", "src/benchmark.py"]
