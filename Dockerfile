FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for hdbscan
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline and frontend
COPY pipeline/ pipeline/
COPY frontend/ frontend/
COPY serve.py .

# Create directories for data
RUN mkdir -p exports output

# Default command runs the full pipeline then serves
CMD ["python", "serve.py"]
