"""
FastAPI app with embedded demo data (no database required)
Perfect for DigitalOcean $5/month deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from datetime import datetime, timedelta
import random

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

# Demo data (Hawaiian hotels)
DEMO_HOTELS = [
    {"id": 1, "name": "Aloha Beach Resort", "location": "Waikiki, Honolulu", "rooms": 350, "rating": 4.5},
    {"id": 2, "name": "Maui Paradise Hotel", "location": "Wailea, Maui", "rooms": 280, "rating": 4.7},
    {"id": 3, "name": "Big Island Retreat", "location": "Kona, Big Island", "rooms": 150, "rating": 4.3},
    {"id": 4, "name": "Kauai Garden Resort", "location": "Poipu, Kauai", "rooms": 200, "rating": 4.6},
    {"id": 5, "name": "Lanai Luxury Lodge", "location": "Lanai City, Lanai", "rooms": 75, "rating": 4.8},
]

DEMO_REVIEWS = [
    {"hotel_id": 1, "rating": 5, "text": "Amazing beachfront location! Perfect for families.", "sentiment": "positive"},
    {"hotel_id": 1, "rating": 4, "text": "Great service, but rooms could be updated.", "sentiment": "neutral"},
    {"hotel_id": 2, "rating": 5, "text": "Luxury at its finest. The spa was incredible!", "sentiment": "positive"},
    {"hotel_id": 2, "rating": 3, "text": "Expensive but worth it for special occasions.", "sentiment": "neutral"},
    {"hotel_id": 3, "rating": 4, "text": "Peaceful retreat with stunning volcano views.", "sentiment": "positive"},
    {"hotel_id": 4, "rating": 5, "text": "Hidden gem! Best snorkeling right from the beach.", "sentiment": "positive"},
    {"hotel_id": 5, "rating": 5, "text": "Ultimate luxury experience. Every detail perfect.", "sentiment": "positive"},
]

def generate_forecast_data():
    """Generate realistic tourism forecast data"""
    base_date = datetime.now()
    forecast = []
    
    for i in range(30):  # 30 days
        date = base_date + timedelta(days=i)
        # Simulate seasonal patterns
        base_occupancy = 65 + random.randint(-15, 25)
        base_revenue = 15000 + random.randint(-5000, 10000)
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "occupancy_rate": max(30, min(95, base_occupancy)),
            "revenue": max(8000, base_revenue),
            "bookings": random.randint(45, 85),
            "avg_rate": random.randint(180, 350)
        })
    
    return forecast

@app.get("/")
async def root():
    return RedirectResponse(url="/health")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "message": "🚀 Tourism Analytics Platform by KoinTyme",
        "deployment": "DigitalOcean - Demo Data Mode",
        "hotels": len(DEMO_HOTELS),
        "reviews": len(DEMO_REVIEWS)
    }

@app.get("/api/v1/", response_class=HTMLResponse)
async def landing_page():
    hotel_count = len(DEMO_HOTELS)
    review_count = len(DEMO_REVIEWS)
    avg_rating = sum(r["rating"] for r in DEMO_REVIEWS) / len(DEMO_REVIEWS)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tourism Analytics Platform - KoinTyme</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
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
                <p style="font-size: 1.2em; margin-bottom: 30px;">AI-Powered Insights for Tourism Businesses</p>
                <div style="font-size: 1.1em; color: #ffd700;">✨ Live Demo with Hawaiian Hotel Data ✨</div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{hotel_count}</div>
                    <div>Hawaiian Hotels</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{review_count}</div>
                    <div>Guest Reviews</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_rating:.1f}</div>
                    <div>Average Rating</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">30</div>
                    <div>Day Forecast</div>
                </div>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>🏨 Hotel Analytics</h3>
                    <p>Track performance across {hotel_count} Hawaiian properties with real-time occupancy and revenue data.</p>
                    <a href="/api/v1/hotels" class="btn">View Hotels</a>
                </div>
                
                <div class="feature-card">
                    <h3>💭 Sentiment Analysis</h3>
                    <p>AI-powered analysis of {review_count} guest reviews with sentiment scoring and insights.</p>
                    <a href="/api/v1/reviews" class="btn">View Reviews</a>
                </div>
                
                <div class="feature-card">
                    <h3>📈 Demand Forecasting</h3>
                    <p>30-day predictive analytics for occupancy, revenue, and booking trends.</p>
                    <a href="/api/v1/forecast" class="btn">View Forecast</a>
                </div>
                
                <div class="feature-card">
                    <h3>🤖 AI Chatbot</h3>
                    <p>Multilingual tourist assistance with Hawaiian tourism expertise.</p>
                    <a href="/api/v1/chat-demo" class="btn">Try Chatbot</a>
                </div>
            </div>
            
            <div class="kointyme">
                <h2>🚀 Engineered & Maintained by KoinTyme</h2>
                <p>Leading provider of AI-powered analytics solutions for the tourism industry. Our platform combines machine learning, natural language processing, and predictive analytics to help businesses maximize revenue and guest satisfaction.</p>
                <p><strong>Enterprise Solutions • Custom Integrations • 24/7 Support</strong></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/v1/hotels")
async def get_hotels():
    return {"hotels": DEMO_HOTELS, "total": len(DEMO_HOTELS)}

@app.get("/api/v1/reviews")
async def get_reviews():
    return {"reviews": DEMO_REVIEWS, "total": len(DEMO_REVIEWS)}

@app.get("/api/v1/forecast")
async def get_forecast():
    return {"forecast": generate_forecast_data(), "days": 30}

@app.get("/api/v1/chat-demo")
async def chat_demo():
    return {
        "message": "Aloha! Welcome to Hawaii! 🌺",
        "responses": [
            "What are the best beaches in Waikiki?",
            "Recommend activities for families",
            "Where can I find authentic Hawaiian food?",
            "What's the weather like in December?"
        ],
        "languages": ["English", "Japanese", "Chinese", "Spanish", "Portuguese"]
    }

@app.get("/docs")
async def custom_docs():
    return RedirectResponse(url="/api/v1/")

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "app-with-demo-data:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )