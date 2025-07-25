FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scraper/ ./scraper/
COPY frontend/ ./frontend/

# Create directories for templates and static files
RUN mkdir -p frontend/templates frontend/static

WORKDIR /app/frontend

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]