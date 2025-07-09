#!/bin/bash

echo "Starting BHSI Backend..."

# Check if we're in the right directory
echo "Current directory: $(pwd)"
echo "Contents:"
ls -la

# Check Python version
echo "Python version:"
python --version

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found!"
    exit 1
fi

# Check if app directory exists
if [ ! -d "app" ]; then
    echo "ERROR: app directory not found!"
    exit 1
fi

# Create necessary directories
mkdir -p app/db

# Test imports
echo "Testing imports..."
python -c "
try:
    from app.core.config import settings
    print('✅ Config imported successfully')
except Exception as e:
    print(f'❌ Config import failed: {e}')
    exit(1)

try:
    from app.api.v1.router import api_router
    print('✅ API router imported successfully')
except Exception as e:
    print(f'❌ API router import failed: {e}')
    exit(1)

try:
    from main import app
    print('✅ Main app imported successfully')
except Exception as e:
    print(f'❌ Main app import failed: {e}')
    exit(1)
"

# Start the application
echo "Starting uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers 

