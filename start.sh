#!/bin/bash
set -e

echo "🌺 Starting Tourism Analytics Platform..."
echo "🚀 Engineered by KoinTyme"

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Run migrations (Railway might not have database ready immediately)
echo "Running database migrations..."
python -c "
import asyncio
import asyncpg
import os
import time

async def wait_for_db():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('No DATABASE_URL found, skipping migration')
        return
    
    print('Waiting for database connection...')
    for i in range(30):  # Wait up to 30 seconds
        try:
            conn = await asyncpg.connect(db_url)
            await conn.close()
            print('Database connected!')
            break
        except Exception as e:
            print(f'Database not ready ({i+1}/30): {e}')
            time.sleep(1)
    else:
        print('Database connection timeout')

if __name__ == '__main__':
    asyncio.run(wait_for_db())
" || echo "Database check failed, continuing..."

# Run Alembic migrations
alembic upgrade head || echo "Migration failed, continuing..."

# Start the application
echo "Starting FastAPI server..."
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 30