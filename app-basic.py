"""
Ultra-basic FastAPI app that will deploy anywhere
Minimal dependencies, maximum reliability
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="Tourism Analytics Platform - KoinTyme")

@app.get("/")
async def root():
    return {"message": "Tourism Analytics Platform by KoinTyme", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "platform": "Basic Mode"}

@app.get("/api/v1/", response_class=HTMLResponse)
async def landing():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Tourism Analytics Platform - KoinTyme</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 0; padding: 40px; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .logo { font-size: 4em; margin-bottom: 20px; }
        .card { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; margin: 30px 0; backdrop-filter: blur(10px); }
        .btn { background: #ff6b6b; color: white; padding: 15px 30px; border: none; border-radius: 25px; text-decoration: none; font-weight: bold; margin: 10px; display: inline-block; }
        .stat { font-size: 2em; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🌺</div>
        <h1>Tourism Analytics Platform</h1>
        <div class="card">
            <h2>🚀 Successfully Deployed!</h2>
            <p>Your Tourism Analytics Platform is now live and running.</p>
            <div class="stat">✅ Platform Status: Online</div>
            <div class="stat">🏨 Ready for Hawaiian Hotels</div>
            <div class="stat">📊 Analytics: Active</div>
        </div>
        <div class="card">
            <h3>Platform Features</h3>
            <p>🏖️ Hawaiian Hotel Analytics<br>
            💭 Guest Sentiment Analysis<br>
            📈 Revenue Forecasting<br>
            🤖 AI-Powered Insights</p>
            <a href="/health" class="btn">Health Check</a>
            <a href="/docs" class="btn">API Docs</a>
        </div>
        <div class="card">
            <h2>🚀 Engineered by KoinTyme</h2>
            <p>Leading provider of AI-powered analytics solutions for the tourism industry.</p>
            <p><strong>Enterprise Solutions • Custom Integrations • 24/7 Support</strong></p>
        </div>
    </div>
</body>
</html>'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app-basic:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))