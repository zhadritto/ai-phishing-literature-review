FROM python:3.11.9-slim@sha256:8fb099199b9f2d70342674bd9dbccd3ed03a258f26bbd1d556822c6dfc60c317

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY config.json ./
COPY src/ ./src/
COPY data/sample/ ./data/sample/

CMD ["python", "src/benchmark.py"]
