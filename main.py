from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles  # Disabled for Render deployment
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with error handling
    import os
    
    # Check if we're in production without database
    if os.getenv("DATABASE_URL") is None:
        print("🌺 Starting in demo mode with embedded data")
        print("✅ Demo database loaded with Hawaiian hotel data")
    else:
        try:
            await redis_client.initialize()
            print("✅ Redis connected")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
    
    yield
    
    # Shutdown
    try:
        if os.getenv("DATABASE_URL"):
            await redis_client.close()
    except:
        pass


app = FastAPI(
    title="Tourism Analytics Platform",
    description="Comprehensive analytics platform for tourism businesses",
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

# Serve static files - disabled for minimal deployment
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )