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

# Add LibreOffice binaries to PATH for easy calling of soffice
ENV PATH="/usr/lib/libreoffice/program:${PATH}"

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI source code into the container
COPY . .

# Expose port 8000 for Uvicorn
EXPOSE 8000

# Command to run your FastAPI app
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app", "--timeout", "500", "--keep-alive", "5"]
