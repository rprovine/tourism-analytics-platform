#!/bin/bash

# Tourism Analytics Platform - Startup Script
echo "🌺 Starting Tourism Analytics Platform..."

# Set default environment variables if not provided
export PYTHONPATH=/app:${PYTHONPATH}
export PYTHONUNBUFFERED=1

# Wait for database if DATABASE_URL is set
if [ ! -z "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database connection..."
    python -c "
import time
import psycopg2
from urllib.parse import urlparse
import os

db_url = os.getenv('DATABASE_URL')
if db_url:
    result = urlparse(db_url)
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            conn.close()
            print('✅ Database is ready!')
            break
        except:
            retry_count += 1
            print(f'Waiting for database... ({retry_count}/{max_retries})')
            time.sleep(2)
    "
    
    # Run Alembic migrations
    echo "🔄 Running database migrations..."
    alembic upgrade head || echo "⚠️  Migration failed or not needed"
    
    # Seed initial data if needed
    echo "🌱 Checking for initial data..."
    python seed_data.py || echo "⚠️  Seed data already exists or not needed"
else
    echo "📦 Running in demo mode (no database)"
fi

# Create necessary directories
mkdir -p models/sentiment models/forecasting uploads static templates

# Start the FastAPI application
echo "🚀 Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --log-level ${LOG_LEVEL:-info}