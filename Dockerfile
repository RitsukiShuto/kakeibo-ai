# Base image with Playwright pre-installed
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies with retries and longer timeout for unstable networks
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 --retries 5 -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p local logs data/csv reports/graphs reports/Reviews/Kakeibo

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]
