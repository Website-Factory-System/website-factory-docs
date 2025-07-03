FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables will be provided by Railway shared variables

# Expose port 8080 to match Management Hub API expectations
EXPOSE 8080

# Run the FastAPI app
# Use :: for IPv6 dual-stack binding as required by Railway
CMD ["uvicorn", "app:app", "--host", "::", "--port", "8080"]