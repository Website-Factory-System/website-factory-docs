FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for SSH
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add current directory to Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Run the application
# Use Railway's PORT environment variable (defaults to 8000 for local development)
CMD ["python", "app.py"]