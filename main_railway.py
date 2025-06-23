import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)

# Global flag to track initialization
initialization_complete = False

async def initialize_databases():
    """Initialize databases in the background for Railway"""
    global initialization_complete
    try:
        print("🔄 Initializing databases...")
        
        # Initialize Redis first (usually faster)
        await redis_client.initialize()
        print("✅ Redis connected")
        
        # Try database migration (non-blocking)
        try:
            import subprocess
            result = subprocess.run(
                ["alembic", "upgrade", "head"], 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            if result.returncode == 0:
                print("✅ Database migrations completed")
            else:
                print(f"⚠️ Migration warning: {result.stderr}")
        except Exception as e:
            print(f"⚠️ Migration skipped: {e}")
        
        initialization_complete = True
        print("🎉 Platform initialization complete!")
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        # Don't fail - let the app run without databases if needed

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start initialization in background (non-blocking)
    asyncio.create_task(initialize_databases())
    
    # Yield immediately so Railway sees the app as "started"
    yield
    
    # Cleanup
    try:
        await redis_client.close()
    except:
        pass

app = FastAPI(
    title="Tourism Analytics Platform",
    description="🚀 Engineered by KoinTyme - AI-powered analytics for tourism businesses",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/")

@app.get("/health")
async def health_check():
    """Simple health check that always responds quickly for Railway"""
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "platform": "Railway",
        "kointyme": "🚀 Engineered by KoinTyme",
        "initialization": "complete" if initialization_complete else "in_progress"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "main_railway:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )