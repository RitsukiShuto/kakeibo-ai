# Base image with Playwright pre-installed
# This image supports both AMD64 and ARM64
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Set working directory
WORKDIR /app

# Install system dependencies (for cron and others if needed)
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (though the base image has some, we ensure chromium is there)
RUN playwright install chromium

# Copy the rest of the application code
COPY . .

# Create necessary directories
RUN mkdir -p local logs data/csv reports/graphs reports/Reviews/Kakeibo

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden by docker-compose)
CMD ["python", "main.py"]
