# Use a lightweight Python base image
FROM python:3.10.9-slim

# Install LibreOffice and dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-calc \
    fonts-dejavu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add LibreOffice binaries to PATH
ENV PATH="/usr/lib/libreoffice/program:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI source code
COPY . .

# --- Download ONNX model from Azure Blob ---
# ARG to pass the connection string at build time (optional)
ARG AZURE_STORAGE_CONNECTION_STRING
ENV AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING

# Run the download script
RUN python app/utils/docker/download_model.py

# Expose port for Uvicorn
EXPOSE 8000

# Command to run FastAPI with Gunicorn
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app", "--timeout", "500", "--keep-alive", "5"]