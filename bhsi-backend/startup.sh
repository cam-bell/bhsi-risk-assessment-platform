#!/bin/bash

# Memory optimization settings
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/app
export PYTHONMALLOC=malloc
export PYTHONDEVMODE=0
export PYTHONHASHSEED=0

echo "Starting BHSI Backend (Minimal Mode)..."

# Validate core imports before starting
echo "Validating core imports..."
python -c "
import sys
try:
    import uvicorn
    import fastapi
    import sqlalchemy
    import google.cloud.bigquery
    import google.generativeai
    print('✅ All core imports successful')
except ImportError as e:
    print(f'❌ Core import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Unexpected error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Core import validation failed"
    exit 1
fi

# Check ML dependencies (optional)
echo "Checking ML dependencies..."
python -c "
import sys
ml_available = True
missing_ml = []

try:
    import torch
except ImportError:
    missing_ml.append('torch')
    ml_available = False

try:
    import transformers
except ImportError:
    missing_ml.append('transformers')
    ml_available = False

try:
    import spacy
except ImportError:
    missing_ml.append('spacy')
    ml_available = False

try:
    import sentence_transformers
except ImportError:
    missing_ml.append('sentence-transformers')
    ml_available = False

try:
    import chromadb
except ImportError:
    missing_ml.append('chromadb')
    ml_available = False

if ml_available:
    print('✅ All ML dependencies available')
else:
    print(f'⚠️ Some ML dependencies missing: {missing_ml}')
    print('⚠️ Running in minimal mode - ML features will be disabled')
"

echo "✅ Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers 