FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-backend.txt .

RUN pip install --no-cache-dir -r requirements-backend.txt

COPY backend ./backend
COPY ml ./ml
COPY data ./data

ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/models
ENV STORAGE_DIR=/app/storage
ENV TRAIN_DATA=/app/data/churn.csv

RUN mkdir -p /app/models /app/storage

RUN python ./data/generate_dataset.py && \
    python -m ml.train

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]