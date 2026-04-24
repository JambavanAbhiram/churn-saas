FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker caching
COPY requirements-backend.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-backend.txt

# Copy project files
COPY backend ./backend
COPY ml ./ml

# Copy data only if folder exists in repo
COPY data ./data

# Environment variables
ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/models
ENV STORAGE_DIR=/app/storage
ENV TRAIN_DATA=/app/data/churn.csv

# Create required directories
RUN mkdir -p /app/models /app/storage

# Generate dataset and train model
RUN python ./data/generate_dataset.py && \
    python -m ml.train

# Expose FastAPI port
EXPOSE 8000

# Start application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
