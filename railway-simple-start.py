"""
Ultra-simple Railway startup script that always responds to health checks
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import uvicorn

app = FastAPI(
    title="Tourism Analytics Platform",
    description="🚀 Engineered by KoinTyme",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hawaiian Hotels Demo Data
HOTELS = [
    {"name": "Aloha Beach Resort", "location": "Waikiki, Honolulu", "rating": 4.5, "occupancy": 85},
    {"name": "Maui Paradise Hotel", "location": "Wailea, Maui", "rating": 4.7, "occupancy": 92},
    {"name": "Big Island Retreat", "location": "Kona, Big Island", "rating": 4.3, "occupancy": 78},
    {"name": "Kauai Garden Resort", "location": "Poipu, Kauai", "rating": 4.6, "occupancy": 88},
    {"name": "Lanai Luxury Lodge", "location": "Lanai City, Lanai", "rating": 4.8, "occupancy": 95},
]

@app.get("/")
async def root():
    return RedirectResponse(url="/api/v1/")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "platform": "Railway",
        "hotels": len(HOTELS),
        "message": "🚀 Tourism Analytics Platform by KoinTyme"
    }

@app.get("/api/v1/", response_class=HTMLResponse)
async def landing_page():
    total_rooms = sum([350, 280, 150, 200, 75])  # Hotel room counts
    avg_occupancy = sum(h["occupancy"] for h in HOTELS) / len(HOTELS)
    avg_rating = sum(h["rating"] for h in HOTELS) / len(HOTELS)
    
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
        .hotel-list {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 30px 0; }}
        .hotel-item {{ background: rgba(255,255,255,0.1); padding: 20px; margin: 15px 0; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; }}
        .btn {{ display: inline-block; background: #ff6b6b; color: white; padding: 15px 30px; border: none; border-radius: 25px; text-decoration: none; font-weight: bold; margin: 10px; }}
        .btn:hover {{ background: #ff5252; }}
        .kointyme {{ background: rgba(255,255,255,0.2); padding: 30px; border-radius: 15px; margin-top: 40px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🌺</div>
            <h1>Tourism Analytics Platform</h1>
            <p style="font-size: 1.2em;">AI-Powered Insights for Tourism Businesses</p>
            <div style="color: #ffd700; font-size: 1.1em;">✨ Live on Railway with Hawaiian Hotel Data ✨</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(HOTELS)}</div>
                <div>Hawaiian Hotels</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_rooms}</div>
                <div>Total Rooms</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_occupancy:.0f}%</div>
                <div>Avg Occupancy</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_rating:.1f}</div>
                <div>Average Rating</div>
            </div>
        </div>
        
        <div class="hotel-list">
            <h2>🏨 Featured Hawaiian Hotels</h2>
            {''.join(f'''
            <div class="hotel-item">
                <div>
                    <strong>{hotel["name"]}</strong><br>
                    <small>{hotel["location"]}</small>
                </div>
                <div style="text-align: right;">
                    <div>Rating: {hotel["rating"]}/5 ⭐</div>
                    <div>Occupancy: {hotel["occupancy"]}%</div>
                </div>
            </div>
            ''' for hotel in HOTELS)}
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="/health" class="btn">📊 System Status</a>
            <a href="/docs" class="btn">📚 API Documentation</a>
        </div>
        
        <div class="kointyme">
            <h2>🚀 Engineered & Maintained by KoinTyme</h2>
            <p>Leading provider of AI-powered analytics solutions for the tourism industry. Our platform combines cutting-edge technology with deep industry expertise to deliver actionable insights that drive revenue growth and enhance guest satisfaction.</p>
            <p><strong>Enterprise Solutions • Custom Integrations • 24/7 Support</strong></p>
            <p>Estimated Daily Revenue: <strong>${int(total_rooms * avg_occupancy * 2.5):,}</strong> across all properties</p>
            <div style="margin-top: 20px; font-size: 0.9em; opacity: 0.8;">
                Successfully deployed on Railway • Health Check: ✅ Active
            </div>
        </div>
    </div>
</body>
</html>'''

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("railway-simple-start:app", host="0.0.0.0", port=port, log_level="info")