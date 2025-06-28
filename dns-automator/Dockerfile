FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set dummy environment variables for API mode
ENV SUPABASE_URL=https://placeholder.supabase.co
ENV SUPABASE_SERVICE_KEY=placeholder-key
ENV API_MODE=true

# Expose port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]