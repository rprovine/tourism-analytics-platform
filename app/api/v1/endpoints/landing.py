from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Get the correct templates directory (go up to project root)
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/", response_class=HTMLResponse)
async def landing_page():
    """Main landing page for the Tourism Analytics Platform"""
    
    # Read the HTML file directly since we have a static template
    try:
        with open(os.path.join(templates_dir, "landing.html"), "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback content if template file not found
        fallback_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🌺 Tourism Analytics Platform</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="jumbotron bg-primary text-white p-5 rounded">
                    <h1 class="display-4">🌺 Tourism Analytics Platform</h1>
                    <p class="lead">Welcome to your comprehensive Hawaiian hotel analytics dashboard</p>
                    <div class="mb-3">
                        <span class="badge bg-light text-dark fs-6 py-2 px-3">
                            🚀 Engineered by KoinTyme Innovation
                        </span>
                    </div>
                    <hr class="my-4">
                    <div class="row">
                        <div class="col-md-3">
                            <a class="btn btn-light btn-lg m-2" href="/docs" role="button">
                                📚 API Documentation
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a class="btn btn-success btn-lg m-2" href="http://localhost:8501" target="_blank" role="button">
                                📊 Interactive Dashboard
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a class="btn btn-warning btn-lg m-2" href="/api/v1/health/" role="button">
                                ❤️ Health Check
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>🏨 Hawaiian Hotels</h5>
                            </div>
                            <div class="card-body">
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item">🏖️ Aloha Resort Waikiki</li>
                                    <li class="list-group-item">🌊 Maui Beach Hotel & Spa</li>
                                    <li class="list-group-item">🌋 Kona Village Resort</li>
                                    <li class="list-group-item">✨ Halekulani Luxury Hotel</li>
                                    <li class="list-group-item">🏔️ Napali Coast Inn</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>🚀 Platform Features</h5>
                            </div>
                            <div class="card-body">
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item">💭 Sentiment Analysis</li>
                                    <li class="list-group-item">📈 Demand Forecasting</li>
                                    <li class="list-group-item">🤖 Multilingual Chatbot</li>
                                    <li class="list-group-item">👥 Lead Management</li>
                                    <li class="list-group-item">📊 Business Dashboards</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=fallback_html)