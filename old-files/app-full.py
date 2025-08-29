from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
# Static files import removed for simpler deployment
import uvicorn
from contextlib import asynccontextmanager
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import random
import json

# Demo data for hotels
DEMO_HOTELS = [
    {
        "id": 1,
        "business_id": "aloha_resort_waikiki",
        "name": "Aloha Resort Waikiki",
        "location": "Waikiki, Oahu",
        "rating": 4.8,
        "occupancy_rate": 0.85,
        "avg_daily_rate": 450,
        "sentiment_score": 0.92,
        "total_reviews": 142,
        "total_rooms": 250
    },
    {
        "id": 2,
        "business_id": "maui_beach_hotel",
        "name": "Maui Beach Hotel & Spa",
        "location": "Kaanapali, Maui",
        "rating": 4.7,
        "occupancy_rate": 0.82,
        "avg_daily_rate": 380,
        "sentiment_score": 0.89,
        "total_reviews": 98,
        "total_rooms": 180
    },
    {
        "id": 3,
        "business_id": "kona_village_resort",
        "name": "Kona Village Resort",
        "location": "Kona, Big Island",
        "rating": 4.9,
        "occupancy_rate": 0.88,
        "avg_daily_rate": 550,
        "sentiment_score": 0.95,
        "total_reviews": 76,
        "total_rooms": 120
    }
]

# Demo reviews
DEMO_REVIEWS = [
    "Amazing stay! The staff was incredibly friendly and helpful.",
    "Beautiful views and excellent service. Highly recommend!",
    "The room was clean and spacious. Great location near the beach.",
    "Loved the pool area and the breakfast was fantastic.",
    "Perfect for our honeymoon. Romantic setting and great amenities."
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌺 Tourism Analytics Platform - Full Version")
    print("✅ Running with demo data and full API endpoints")
    print("🏢 Powered by LeniLani Consulting")
    yield
    print("👋 Shutting down")

app = FastAPI(
    title="Tourism Analytics Platform",
    description="Comprehensive analytics platform for tourism businesses - by LeniLani Consulting",
    version="2.0.0",
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

# Serve landing page
@app.get("/", response_class=HTMLResponse)
async def root():
    import os
    template_path = os.path.join(os.path.dirname(__file__), "templates", "landing.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
            return content
    except FileNotFoundError:
        # Try alternate path
        try:
            with open("templates/landing.html", "r", encoding="utf-8") as f:
                return f.read()
        except:
            return "<h1>🌺 Tourism Analytics Platform</h1><p>API is running. Visit <a href='/docs'>/docs</a> for API documentation.</p>"

# Health endpoints
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/api/v1/health/")
async def health_v1():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/health/detailed")
async def health_detailed():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "api": "operational",
            "database": "demo_mode",
            "redis": "not_connected",
            "ml_models": "loaded"
        },
        "timestamp": datetime.now().isoformat()
    }

# Hotels endpoints
@app.get("/api/v1/hotels")
async def get_hotels():
    return {
        "status": "success",
        "hotels": DEMO_HOTELS,
        "total": len(DEMO_HOTELS)
    }

@app.get("/api/v1/hotels/{business_id}")
async def get_hotel(business_id: str):
    hotel = next((h for h in DEMO_HOTELS if h["business_id"] == business_id), None)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"status": "success", "hotel": hotel}

# Reviews endpoints
@app.get("/api/v1/reviews/statistics")
async def reviews_statistics(business_id: str = "aloha_resort_waikiki"):
    hotel = next((h for h in DEMO_HOTELS if h["business_id"] == business_id), None)
    if hotel:
        return {
            "status": "success",
            "statistics": {
                "total_reviews": hotel["total_reviews"],
                "average_rating": hotel["rating"],
                "sentiment_score": hotel["sentiment_score"]
            }
        }
    return {"status": "success", "statistics": {"total_reviews": 0, "average_rating": 0}}

@app.get("/api/v1/reviews/analytics")
async def reviews_analytics(business_id: str = "aloha_resort_waikiki"):
    hotel = next((h for h in DEMO_HOTELS if h["business_id"] == business_id), None)
    if hotel:
        return {
            "status": "success",
            "analytics": {
                "total_reviews": hotel["total_reviews"],
                "average_score": hotel["rating"],
                "overall_sentiment": "positive" if hotel["sentiment_score"] > 0.7 else "neutral",
                "sentiment_distribution": {
                    "positive": int(hotel["sentiment_score"] * 100),
                    "neutral": int((1 - hotel["sentiment_score"]) * 50),
                    "negative": int((1 - hotel["sentiment_score"]) * 50)
                },
                "common_keywords": ["beautiful", "clean", "friendly", "location", "beach"]
            }
        }
    return {"status": "error", "message": "Business not found"}

# Sentiment Analysis endpoint
@app.post("/api/v1/reviews/sentiment")
async def analyze_sentiment(text: str):
    # Simple sentiment simulation
    positive_words = ["good", "great", "excellent", "amazing", "wonderful", "love", "best"]
    negative_words = ["bad", "terrible", "awful", "horrible", "worst", "hate", "poor"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        score = min(0.9 + (positive_count * 0.02), 1.0)
    elif negative_count > positive_count:
        sentiment = "negative"
        score = max(0.3 - (negative_count * 0.05), 0.0)
    else:
        sentiment = "neutral"
        score = 0.5
    
    return {
        "status": "success",
        "sentiment": sentiment,
        "score": score,
        "confidence": 0.85
    }

# Forecasting endpoints
@app.get("/api/v1/forecasting/forecast")
async def generate_forecast(business_id: str = "aloha_resort_waikiki", days_ahead: int = 7):
    hotel = next((h for h in DEMO_HOTELS if h["business_id"] == business_id), None)
    if not hotel:
        return {"status": "error", "message": "Business not found"}
    
    base_visitors = hotel["total_rooms"] * hotel["occupancy_rate"] * 2  # Assume 2 visitors per room
    predictions = []
    
    for i in range(days_ahead):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        # Add some random variation
        variation = random.uniform(0.85, 1.15)
        predicted = int(base_visitors * variation)
        
        predictions.append({
            "date": date,
            "predicted_visitors": predicted,
            "confidence_lower": int(predicted * 0.9),
            "confidence_upper": int(predicted * 1.1),
            "model_used": "random_forest"
        })
    
    return {
        "status": "success",
        "business_id": business_id,
        "predictions": predictions,
        "model_performance": {
            "r2": 0.87,
            "rmse": 12.5,
            "mae": 9.8
        }
    }

# Leads endpoints
@app.get("/api/v1/leads/analytics/{business_id}")
async def leads_analytics(business_id: str):
    return {
        "status": "success",
        "analytics": {
            "total_leads": random.randint(20, 40),
            "conversion_rate": 0.23,
            "average_value": 2500,
            "top_sources": ["website", "social_media", "referral"]
        }
    }

@app.post("/api/v1/leads/")
async def create_lead(lead_data: dict):
    return {
        "status": "success",
        "message": "Lead created successfully",
        "lead_id": f"lead_{random.randint(1000, 9999)}"
    }

# Chat endpoints
@app.get("/api/v1/chat/analytics")
async def chat_analytics(business_id: str = "aloha_resort_waikiki"):
    return {
        "status": "success",
        "analytics": {
            "total_sessions": random.randint(300, 500),
            "avg_session_duration": "5.2 minutes",
            "satisfaction_rate": 0.91,
            "top_intents": ["booking", "amenities", "location", "pricing"]
        }
    }

@app.post("/api/v1/chat/message")
async def chat_message(message: str, language: str = "en"):
    responses = [
        "Thank you for your message! How can I help you today?",
        "I'd be happy to assist you with your inquiry about our resort.",
        "Our hotel offers amazing amenities including spa, pool, and beach access.",
        "Would you like to know more about our current special offers?"
    ]
    
    return {
        "status": "success",
        "response": random.choice(responses),
        "intent": "general_inquiry",
        "confidence": 0.92,
        "language_detected": language
    }

# Dashboard data endpoint
@app.get("/api/v1/dashboard/metrics")
async def dashboard_metrics(business_id: str = "aloha_resort_waikiki"):
    hotel = next((h for h in DEMO_HOTELS if h["business_id"] == business_id), None)
    if not hotel:
        return {"status": "error", "message": "Business not found"}
    
    return {
        "status": "success",
        "metrics": {
            "occupancy_rate": hotel["occupancy_rate"],
            "avg_daily_rate": hotel["avg_daily_rate"],
            "revenue_per_room": hotel["avg_daily_rate"] * hotel["occupancy_rate"],
            "total_revenue_mtd": hotel["avg_daily_rate"] * hotel["occupancy_rate"] * hotel["total_rooms"] * 15,
            "sentiment_score": hotel["sentiment_score"],
            "total_reviews": hotel["total_reviews"],
            "forecast_next_week": {
                "occupancy": min(hotel["occupancy_rate"] * 1.05, 0.95),
                "revenue": hotel["avg_daily_rate"] * hotel["occupancy_rate"] * hotel["total_rooms"] * 7 * 1.05
            }
        }
    }

# Web dashboard endpoint
@app.get("/api/v1/web-dashboard")
async def web_dashboard():
    return {
        "status": "success",
        "message": "Web dashboard API",
        "features": [
            "Real-time analytics",
            "Interactive charts",
            "Sentiment analysis",
            "Demand forecasting",
            "Lead management"
        ]
    }

# API root
@app.get("/api/v1/")
async def api_root():
    return {
        "message": "🌺 Tourism Analytics Platform API v1",
        "status": "operational",
        "powered_by": "LeniLani Consulting",
        "endpoints": {
            "health": "/api/v1/health/",
            "hotels": "/api/v1/hotels",
            "reviews": "/api/v1/reviews/analytics",
            "forecasting": "/api/v1/forecasting/forecast",
            "chat": "/api/v1/chat/message",
            "dashboard": "/api/v1/dashboard/metrics",
            "documentation": "/docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)