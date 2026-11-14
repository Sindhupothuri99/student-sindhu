FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-lock.txt .

RUN pip install --no-cache-dir --only-binary=:all: -r requirements-lock.txt

COPY app/ ./app/
COPY config.py run.py ./

RUN mkdir -p /app/instance

EXPOSE 5000

CMD ["gunicorn", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:5000", "run:app"]
