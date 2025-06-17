#!/bin/bash

echo "🚀 Starting BHSI Corporate Risk Assessment API (Production)..."

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start the application with Gunicorn for production
echo "🎯 Starting production server on http://0.0.0.0:8000"
echo "📖 API Documentation available at http://localhost:8000/docs"
echo "🔍 Main search endpoint: POST http://localhost:8000/api/v1/search"
echo ""

# Use Gunicorn for production deployment
gunicorn main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --preload 