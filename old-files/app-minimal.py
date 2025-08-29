"""
Ultra-minimal FastAPI app for DigitalOcean deployment
Just the essentials with embedded Hawaiian hotel data
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from datetime import datetime, timedelta
import random
import os

app = FastAPI(
    title="Tourism Analytics Platform",
    description="🚀 Engineered by KoinTyme - AI-powered analytics for tourism businesses",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hawaiian Hotels Demo Data
HOTELS = [
    {"id": 1, "name": "Aloha Beach Resort", "location": "Waikiki, Honolulu", "rooms": 350, "rating": 4.5, "occupancy": 85},
    {"id": 2, "name": "Maui Paradise Hotel", "location": "Wailea, Maui", "rooms": 280, "rating": 4.7, "occupancy": 92},
    {"id": 3, "name": "Big Island Retreat", "location": "Kona, Big Island", "rooms": 150, "rating": 4.3, "occupancy": 78},
    {"id": 4, "name": "Kauai Garden Resort", "location": "Poipu, Kauai", "rooms": 200, "rating": 4.6, "occupancy": 88},
    {"id": 5, "name": "Lanai Luxury Lodge", "location": "Lanai City, Lanai", "rooms": 75, "rating": 4.8, "occupancy": 95},
]

REVIEWS = [
    {"hotel": "Aloha Beach Resort", "rating": 5, "text": "Amazing beachfront location! Perfect for families.", "sentiment": "positive"},
    {"hotel": "Maui Paradise Hotel", "rating": 5, "text": "Luxury at its finest. The spa was incredible!", "sentiment": "positive"},
    {"hotel": "Big Island Retreat", "rating": 4, "text": "Peaceful retreat with stunning volcano views.", "sentiment": "positive"},
    {"hotel": "Kauai Garden Resort", "rating": 5, "text": "Hidden gem! Best snorkeling right from the beach.", "sentiment": "positive"},
    {"hotel": "Lanai Luxury Lodge", "rating": 5, "text": "Ultimate luxury experience. Every detail perfect.", "sentiment": "positive"},
]

@app.get("/")
async def root():
    return RedirectResponse(url="/api/v1/")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "message": "🚀 Tourism Analytics Platform by KoinTyme",
        "deployment": "DigitalOcean - Minimal Mode",
        "hotels": len(HOTELS),
        "reviews": len(REVIEWS)
    }

@app.get("/api/v1/hotels")
async def get_hotels():
    return {"hotels": HOTELS, "total": len(HOTELS)}

@app.get("/api/v1/reviews")
async def get_reviews():
    return {"reviews": REVIEWS, "total": len(REVIEWS)}

@app.get("/api/v1/analytics")
async def get_analytics():
    total_rooms = sum(h["rooms"] for h in HOTELS)
    avg_occupancy = sum(h["occupancy"] for h in HOTELS) / len(HOTELS)
    avg_rating = sum(r["rating"] for r in REVIEWS) / len(REVIEWS)
    
    return {
        "total_hotels": len(HOTELS),
        "total_rooms": total_rooms,
        "average_occupancy": round(avg_occupancy, 1),
        "average_rating": round(avg_rating, 1),
        "total_reviews": len(REVIEWS),
        "revenue_estimate": round(total_rooms * avg_occupancy * 250 / 100, 2)
    }

@app.get("/api/v1/", response_class=HTMLResponse)
async def landing_page():
    stats = await get_analytics()
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Tourism Analytics Platform - KoinTyme</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ text-align: center; margin-bottom: 50px; }}
        .logo {{ font-size: 4em; margin-bottom: 20px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; margin: 40px 0; }}
        .stat-card {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px); }}
        .stat-number {{ font-size: 3em; font-weight: bold; margin-bottom: 10px; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin: 50px 0; }}
        .feature-card {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }}
        .btn {{ display: inline-block; background: #ff6b6b; color: white; padding: 15px 30px; border: none; border-radius: 25px; text-decoration: none; font-weight: bold; margin: 10px; cursor: pointer; }}
        .btn:hover {{ background: #ff5252; }}
        .kointyme {{ background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin-top: 40px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🌺</div>
            <h1>Tourism Analytics Platform</h1>
            <p style="font-size: 1.2em;">AI-Powered Insights for Tourism Businesses</p>
            <div style="color: #ffd700;">✨ Live Demo with Hawaiian Hotel Data ✨</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{stats["total_hotels"]}</div>
                <div>Hawaiian Hotels</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats["total_rooms"]}</div>
                <div>Total Rooms</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats["average_occupancy"]}%</div>
                <div>Avg Occupancy</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats["average_rating"]}</div>
                <div>Average Rating</div>
            </div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>🏨 Hotel Analytics</h3>
                <p>Real-time performance tracking across {stats["total_hotels"]} Hawaiian properties.</p>
                <a href="/api/v1/hotels" class="btn">View Hotels</a>
            </div>
            
            <div class="feature-card">
                <h3>💭 Guest Reviews</h3>
                <p>Comprehensive analysis of {stats["total_reviews"]} guest experiences.</p>
                <a href="/api/v1/reviews" class="btn">View Reviews</a>
            </div>
            
            <div class="feature-card">
                <h3>📊 Analytics Dashboard</h3>
                <p>Revenue insights and performance metrics.</p>
                <a href="/api/v1/analytics" class="btn">View Analytics</a>
            </div>
            
            <div class="feature-card">
                <h3>📚 API Documentation</h3>
                <p>Full REST API for integration and development.</p>
                <a href="/docs" class="btn">API Docs</a>
            </div>
        </div>
        
        <div class="kointyme">
            <h2>🚀 Engineered & Maintained by KoinTyme</h2>
            <p>Leading provider of AI-powered analytics solutions for the tourism industry. Our platform delivers actionable insights to maximize revenue and enhance guest satisfaction.</p>
            <p><strong>Enterprise Solutions • Custom Integrations • 24/7 Support</strong></p>
            <p>Revenue Estimate: <strong>${stats["revenue_estimate"]:,.0f}/day</strong> across all properties</p>
        </div>
    </div>
</body>
</html>'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app-minimal:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))