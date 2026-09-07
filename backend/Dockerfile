FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for XGBoost, UMAP, FAISS, psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the full backend source
COPY . .

# Create a writable directory for the SQLite database (Railway persistent volume)
RUN mkdir -p /data

# Expose port (Railway injects $PORT at runtime)
EXPOSE 8000

# Start with gunicorn for production; fallback to uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
