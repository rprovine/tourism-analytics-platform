from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

# Minimal demo data
DEMO_HOTELS = [
    {
        "id": 1,
        "name": "Grand Wailea Resort",
        "location": "Maui",
        "rating": 4.8,
        "occupancy_rate": 0.85,
        "avg_daily_rate": 450,
        "sentiment_score": 0.92
    },
    {
        "id": 2,
        "name": "Four Seasons Resort Oahu",
        "location": "Oahu",
        "rating": 4.9,
        "occupancy_rate": 0.88,
        "avg_daily_rate": 550,
        "sentiment_score": 0.95
    },
    {
        "id": 3,
        "name": "Montage Kapalua Bay",
        "location": "Maui",
        "rating": 4.7,
        "occupancy_rate": 0.82,
        "avg_daily_rate": 480,
        "sentiment_score": 0.89
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌺 Tourism Analytics Platform - Demo Mode")
    print("✅ Running with embedded demo data")
    yield
    print("👋 Shutting down")

app = FastAPI(
    title="Tourism Analytics Platform",
    description="Comprehensive analytics platform for tourism businesses",
    version="1.0.0",
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

@app.get("/")
async def root():
    return {
        "message": "🌺 Welcome to Tourism Analytics Platform",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "hotels": "/api/v1/hotels",
            "analytics": "/api/v1/analytics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "mode": "demo"}

@app.get("/api/v1/hotels")
async def get_hotels():
    return {"hotels": DEMO_HOTELS, "total": len(DEMO_HOTELS)}

@app.get("/api/v1/analytics")
async def get_analytics():
    return {
        "summary": {
            "total_hotels": len(DEMO_HOTELS),
            "avg_occupancy": sum(h["occupancy_rate"] for h in DEMO_HOTELS) / len(DEMO_HOTELS),
            "avg_rate": sum(h["avg_daily_rate"] for h in DEMO_HOTELS) / len(DEMO_HOTELS),
            "avg_sentiment": sum(h["sentiment_score"] for h in DEMO_HOTELS) / len(DEMO_HOTELS)
        },
        "trends": {
            "occupancy_trend": "increasing",
            "rate_trend": "stable",
            "sentiment_trend": "positive"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main-minimal:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )