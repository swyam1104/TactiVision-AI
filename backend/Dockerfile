FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for compiling numerical modules (XGBoost, UMAP, FAISS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI app by default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
