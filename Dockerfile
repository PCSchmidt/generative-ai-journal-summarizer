# Railway Docker deployment for AI Journal Summarizer
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (g++ needed for faiss-cpu compilation)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy main application and modules
COPY main.py .
COPY rag/ rag/

# Create data directory for journal SQLite + FAISS index
RUN mkdir -p data

# Railway health checks target 8080 by default for this service.
EXPOSE 8080

# Start the application on the same port configured in Railway networking.
CMD uvicorn main:app --host 0.0.0.0 --port 8080
