#!/bin/bash

echo "🚀 Starting BHSI Corporate Risk Assessment API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start the application with uvicorn
echo "🎯 Starting application on http://localhost:8000"
echo "📖 API Documentation available at http://localhost:8000/docs"
echo "🔍 Main search endpoint: POST http://localhost:8000/api/v1/search"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 