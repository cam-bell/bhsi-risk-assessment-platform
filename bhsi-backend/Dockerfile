# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first to leverage Docker cache
COPY requirements-minimal.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --no-deps -r requirements-minimal.txt \
    && pip cache purge

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/app/db

# Set environment variables to reduce memory usage
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV PYTHONMALLOC=malloc
ENV PYTHONDEVMODE=0
ENV PYTHONHASHSEED=0

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use startup script
CMD ["./startup.sh"] 