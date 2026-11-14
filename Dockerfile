FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-lock.txt .

RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r requirements-lock.txt

COPY app/ ./app/
COPY config.py run.py ./

RUN groupadd --system appuser && \
    useradd --system --gid appuser --home-dir /app --no-create-home appuser && \
    mkdir -p /app/instance && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:5000", "run:app"]
