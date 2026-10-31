FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for XGBoost, UMAP, FAISS, psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    gcc \
    g++ \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the full backend source
COPY . .

# Decompress pre-built database if present
RUN if [ -f tactivision.db.gz ]; then gzip -dk tactivision.db.gz; fi

# Ensure SQLite database is writable
RUN chmod 666 tactivision.db 2>/dev/null || true

# Expose port (Render/Railway injects $PORT at runtime)
EXPOSE 8000

# Start with uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
