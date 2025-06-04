#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the FastAPI application with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info 