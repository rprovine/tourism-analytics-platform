"""
Simple FastAPI app without database migrations for Railway deployment
Use this if migrations keep failing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

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

@app.get("/")
async def root():
    return RedirectResponse(url="/health")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "message": "🚀 Tourism Analytics Platform by KoinTyme",
        "deployment": "Railway - No database mode"
    }

@app.get("/api/v1/", response_class=HTMLResponse)
async def landing_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tourism Analytics Platform - KoinTyme</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            .header { text-align: center; margin-bottom: 40px; }
            .logo { font-size: 3em; margin-bottom: 10px; }
            .status { padding: 20px; background: #e8f5e8; border-radius: 8px; margin: 20px 0; }
            .note { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🌺</div>
                <h1>Tourism Analytics Platform</h1>
                <p><strong>🚀 Engineered & Maintained by KoinTyme</strong></p>
            </div>
            
            <div class="status">
                <h3>✅ Deployment Successful!</h3>
                <p>Your Tourism Analytics Platform is now running on Railway.</p>
            </div>
            
            <div class="note">
                <h4>📋 Next Steps:</h4>
                <ol>
                    <li>This is a simplified version without database connections</li>
                    <li>Once this is working, we can add databases back</li>
                    <li>Contact KoinTyme for full feature activation</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin-top: 40px; color: #666;">
                <p>Platform Status: <strong>Online</strong></p>
                <p>Version: 1.0.0 | Deployment: Railway</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "no-migrations:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )