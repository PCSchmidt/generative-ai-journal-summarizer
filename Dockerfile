# Railway Docker deployment for AI Journal Summarizer
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies  
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main application
COPY main.py .

# Railway provides PORT environment variable
EXPOSE $PORT

# Start the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
