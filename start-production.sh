#!/bin/bash

# Tourism Analytics Platform - Production Startup Script
# Runs both FastAPI and Streamlit in a single container
# Engineered by KoinTyme

echo "🌺 Starting Tourism Analytics Platform..."
echo "🚀 Engineered by KoinTyme"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start FastAPI in background
echo "Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 &

# Wait a moment for FastAPI to start
sleep 5

# Start Streamlit dashboard
echo "Starting Streamlit dashboard on port 8501..."
streamlit run app/dashboard/web_dashboard.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --server.runOnSave false &

# Wait for both services to start
sleep 10

# Health check
echo "Checking services health..."
curl -f http://localhost:8000/api/v1/health/ && echo "✅ FastAPI is healthy"

echo "🎉 All services started successfully!"
echo "📊 FastAPI: http://localhost:8000"
echo "📈 Streamlit: http://localhost:8501"

# Keep the container running
wait