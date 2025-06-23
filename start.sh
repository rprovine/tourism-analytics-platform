#!/bin/bash

echo "🌺 Starting Tourism Analytics Platform..."
echo "🚀 Engineered by KoinTyme"

# Railway-specific fast startup
if [ -n "$RAILWAY_ENVIRONMENT" ] || [ -n "$DATABASE_URL" ]; then
    echo "🚂 Railway environment detected - fast startup mode"
    PORT=${PORT:-8000}
    echo "Starting server immediately on port $PORT..."
    exec uvicorn main_railway:app --host 0.0.0.0 --port $PORT --workers 1
else
    echo "🏠 Local environment detected"
    echo "Running database migrations..."
    alembic upgrade head || echo "Migration failed, continuing..."
    PORT=${PORT:-8000}
    echo "Starting server on port $PORT..."
    exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
fi