FROM python:3.11-slim

# Install Tesseract OCR and required system libraries
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Render provides the PORT environment variable
CMD gunicorn --timeout 120 --workers 1 --bind 0.0.0.0:$PORT app:app