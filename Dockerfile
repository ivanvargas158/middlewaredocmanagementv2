FROM python:3.10.9-slim

# Install LibreOffice and dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-calc \
    fonts-dejavu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/libreoffice/program:${PATH}"
WORKDIR /app

# Copy requirements first for Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure local cache directory exists
RUN mkdir -p .cache/models

# Pre-download ONNX model at build time (Azure Blob)
ARG AZURE_STORAGE_CONNECTION_STRING
RUN python -c "\
from azure.storage.blob import BlobServiceClient; \
from pathlib import Path; import os; \
CACHE_DIR = Path('./.cache/models'); CACHE_DIR.mkdir(parents=True, exist_ok=True); \
BLOB_NAME='llama-prompt-guard-onnx/model.onnx'; \
client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING')).get_blob_client('models', BLOB_NAME); \
with open(CACHE_DIR/BLOB_NAME.split('/')[-1], 'wb') as f: f.write(client.download_blob().readall()) \
"

EXPOSE 8000

# Gunicorn with 2 workers, tuned for large models
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app", "--timeout", "500", "--keep-alive", "5"]