# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables for memory optimization
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TRANSFORMERS_CACHE=/tmp/transformers_cache
ENV TORCH_HOME=/tmp/torch_cache
ENV HF_HOME=/tmp/hf_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/transformers_cache /tmp/torch_cache /tmp/hf_cache

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Validating imports..."\n\
python -c "import uvicorn; print(\"✓ uvicorn imported successfully\")"\n\
python -c "import fastapi; print(\"✓ fastapi imported successfully\")"\n\
echo "Starting application..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["/app/start.sh"] 