from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Tourism Analytics Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    # Read and serve the landing page
    try:
        with open("templates/landing.html", "r") as f:
            return f.read()
    except:
        return "<h1>🌺 Tourism Analytics Platform</h1><p>API is running. Visit <a href='/docs'>/docs</a> for API documentation.</p>"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/health/detailed")
async def health_detailed():
    return {"status": "healthy", "services": {"api": "running", "database": "demo_mode"}}

@app.get("/api/v1/reviews/statistics")
async def reviews_stats(business_id: str = "aloha_resort_waikiki"):
    return {"status": "success", "statistics": {"total_reviews": 142, "average_rating": 4.7}}

@app.get("/api/v1/leads/analytics/{business_id}")
async def leads_analytics(business_id: str):
    return {"status": "success", "analytics": {"total_leads": 28}}

@app.get("/api/v1/chat/analytics")
async def chat_analytics(business_id: str = "aloha_resort_waikiki"):
    return {"status": "success", "analytics": {"total_sessions": 384}}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)