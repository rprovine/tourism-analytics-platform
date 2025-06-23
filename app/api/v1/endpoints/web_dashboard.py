from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard landing page"""
    
    dashboard_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌺 Tourism Analytics Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .dashboard-card { 
                background: white; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                margin: 20px 0;
                padding: 20px;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
            }
            .hotel-btn {
                margin: 5px;
                border-radius: 20px;
            }
            .navbar-brand { font-size: 1.5rem; }
            #loadingSpinner {
                display: none;
                text-align: center;
                padding: 50px;
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <span class="navbar-brand">🌺 Tourism Analytics Dashboard</span>
                <span class="navbar-text">Real-time Hawaiian Hotel Insights</span>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- Hotel Selection -->
            <div class="dashboard-card">
                <h3>🏨 Select Hawaiian Hotel</h3>
                <div class="row">
                    <div class="col-md-12">
                        <button class="btn btn-outline-primary hotel-btn" onclick="loadHotelData('aloha_resort_waikiki', 'Aloha Resort Waikiki')">
                            🏖️ Aloha Resort Waikiki
                        </button>
                        <button class="btn btn-outline-success hotel-btn" onclick="loadHotelData('maui_beach_hotel', 'Maui Beach Hotel & Spa')">
                            🌊 Maui Beach Hotel & Spa
                        </button>
                        <button class="btn btn-outline-info hotel-btn" onclick="loadHotelData('kona_village_resort', 'Kona Village Resort')">
                            🌋 Kona Village Resort
                        </button>
                        <button class="btn btn-outline-warning hotel-btn" onclick="loadHotelData('halekulani_luxury', 'Halekulani Luxury Hotel')">
                            ✨ Halekulani Luxury
                        </button>
                        <button class="btn btn-outline-secondary hotel-btn" onclick="loadHotelData('napali_coast_inn', 'Napali Coast Inn')">
                            🏔️ Napali Coast Inn
                        </button>
                    </div>
                </div>
            </div>

            <!-- Loading Spinner -->
            <div id="loadingSpinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading hotel analytics...</p>
            </div>

            <!-- Selected Hotel Info -->
            <div id="hotelInfo" style="display:none;" class="dashboard-card">
                <h2 id="hotelName">Select a hotel to view analytics</h2>
                <p class="text-muted" id="hotelDescription">Choose from our 5 Hawaiian hotel locations above</p>
            </div>

            <!-- Key Metrics -->
            <div id="metricsSection" style="display:none;">
                <div class="row" id="keyMetrics">
                    <!-- Metrics will be loaded here -->
                </div>
            </div>

            <!-- Charts Section -->
            <div id="chartsSection" style="display:none;">
                <div class="row">
                    <div class="col-md-6">
                        <div class="dashboard-card">
                            <h4>📊 Sentiment Analysis</h4>
                            <div id="sentimentChart" style="height: 400px;"></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="dashboard-card">
                            <h4>📈 Visitor Forecast</h4>
                            <div id="forecastChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="dashboard-card">
                            <h4>💬 Chat Analytics</h4>
                            <div id="chatChart" style="height: 400px;"></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="dashboard-card">
                            <h4>👥 Lead Management</h4>
                            <div id="leadChart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Links -->
            <div class="dashboard-card">
                <h4>🔗 Quick Links</h4>
                <div class="row">
                    <div class="col-md-3">
                        <a href="/docs" class="btn btn-primary w-100" target="_blank">
                            📚 API Documentation
                        </a>
                    </div>
                    <div class="col-md-3">
                        <a href="http://localhost:8501" class="btn btn-success w-100" target="_blank">
                            📊 Advanced Dashboard
                        </a>
                    </div>
                    <div class="col-md-3">
                        <a href="/api/v1/health/" class="btn btn-info w-100" target="_blank">
                            ❤️ Health Check
                        </a>
                    </div>
                    <div class="col-md-3">
                        <button class="btn btn-warning w-100" onclick="refreshData()">
                            🔄 Refresh Data
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentBusinessId = null;
            
            async function loadHotelData(businessId, hotelName) {
                currentBusinessId = businessId;
                
                // Show loading
                document.getElementById('loadingSpinner').style.display = 'block';
                document.getElementById('hotelInfo').style.display = 'none';
                document.getElementById('metricsSection').style.display = 'none';
                document.getElementById('chartsSection').style.display = 'none';
                
                // Update hotel info
                document.getElementById('hotelName').textContent = hotelName;
                document.getElementById('hotelDescription').textContent = `Analytics dashboard for ${hotelName}`;
                
                try {
                    // Load all data in parallel
                    const [sentimentData, metricsData, forecastData] = await Promise.all([
                        fetch(`/api/v1/reviews/analytics?business_id=${businessId}&days=30`).then(r => r.json()),
                        fetch(`/api/v1/dashboard/metrics?business_id=${businessId}&days=30`).then(r => r.json()),
                        fetch(`/api/v1/forecasting/forecast`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ business_id: businessId, days_ahead: 14 })
                        }).then(r => r.json())
                    ]);
                    
                    // Hide loading
                    document.getElementById('loadingSpinner').style.display = 'none';
                    document.getElementById('hotelInfo').style.display = 'block';
                    document.getElementById('metricsSection').style.display = 'block';
                    document.getElementById('chartsSection').style.display = 'block';
                    
                    // Update metrics
                    updateMetrics(sentimentData, metricsData);
                    
                    // Update charts
                    updateSentimentChart(sentimentData);
                    updateForecastChart(forecastData);
                    updateChatChart(businessId);
                    updateLeadChart(businessId);
                    
                } catch (error) {
                    document.getElementById('loadingSpinner').style.display = 'none';
                    alert('Error loading data: ' + error.message);
                }
            }
            
            function updateMetrics(sentimentData, metricsData) {
                const metricsHtml = `
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h3>${sentimentData.analytics?.overall_sentiment || 'N/A'}</h3>
                            <p>Overall Sentiment</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h3>${sentimentData.analytics?.total_reviews || 0}</h3>
                            <p>Total Reviews</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h3>${metricsData.metrics?.visitors?.average_daily?.toFixed(1) || 'N/A'}</h3>
                            <p>Daily Visitors</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h3>$${(metricsData.metrics?.visitors?.total_revenue || 0).toLocaleString()}</h3>
                            <p>Total Revenue</p>
                        </div>
                    </div>
                `;
                document.getElementById('keyMetrics').innerHTML = metricsHtml;
            }
            
            function updateSentimentChart(data) {
                if (!data.analytics?.sentiment_distribution) {
                    document.getElementById('sentimentChart').innerHTML = '<p class="text-center text-muted">No sentiment data available</p>';
                    return;
                }
                
                const dist = data.analytics.sentiment_distribution;
                const sentimentChart = {
                    data: [{
                        values: Object.values(dist),
                        labels: Object.keys(dist),
                        type: 'pie',
                        marker: {
                            colors: ['#28a745', '#ffc107', '#dc3545']
                        }
                    }],
                    layout: {
                        title: 'Sentiment Distribution',
                        height: 350
                    }
                };
                Plotly.newPlot('sentimentChart', sentimentChart.data, sentimentChart.layout);
            }
            
            function updateForecastChart(data) {
                if (!data.predictions) {
                    document.getElementById('forecastChart').innerHTML = '<p class="text-center text-muted">No forecast data available</p>';
                    return;
                }
                
                const dates = data.predictions.map(p => p.date);
                const visitors = data.predictions.map(p => p.predicted_visitors);
                
                const forecastChart = {
                    data: [{
                        x: dates,
                        y: visitors,
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Predicted Visitors',
                        line: { color: '#007bff' }
                    }],
                    layout: {
                        title: '14-Day Visitor Forecast',
                        xaxis: { title: 'Date' },
                        yaxis: { title: 'Visitors' },
                        height: 350
                    }
                };
                Plotly.newPlot('forecastChart', forecastChart.data, forecastChart.layout);
            }
            
            async function updateChatChart(businessId) {
                try {
                    const response = await fetch(`/api/v1/chat/analytics?business_id=${businessId}`);
                    const data = await response.json();
                    
                    if (data.status === 'success' && data.analytics.intent_distribution) {
                        const intents = data.analytics.intent_distribution;
                        const chatChart = {
                            data: [{
                                x: Object.keys(intents),
                                y: Object.values(intents),
                                type: 'bar',
                                marker: { color: '#17a2b8' }
                            }],
                            layout: {
                                title: 'Chat Intent Distribution',
                                height: 350
                            }
                        };
                        Plotly.newPlot('chatChart', chatChart.data, chatChart.layout);
                    } else {
                        document.getElementById('chatChart').innerHTML = '<p class="text-center text-muted">No chat data available</p>';
                    }
                } catch (error) {
                    document.getElementById('chatChart').innerHTML = '<p class="text-center text-muted">Error loading chat data</p>';
                }
            }
            
            async function updateLeadChart(businessId) {
                try {
                    const response = await fetch(`/api/v1/leads/analytics/${businessId}`);
                    const data = await response.json();
                    
                    if (data.status === 'success' && data.analytics.status_distribution) {
                        const status = data.analytics.status_distribution;
                        const leadChart = {
                            data: [{
                                values: Object.values(status),
                                labels: Object.keys(status),
                                type: 'pie',
                                marker: { colors: ['#28a745', '#6c757d', '#ffc107'] }
                            }],
                            layout: {
                                title: 'Lead Status Distribution',
                                height: 350
                            }
                        };
                        Plotly.newPlot('leadChart', leadChart.data, leadChart.layout);
                    } else {
                        document.getElementById('leadChart').innerHTML = '<p class="text-center text-muted">No lead data available</p>';
                    }
                } catch (error) {
                    document.getElementById('leadChart').innerHTML = '<p class="text-center text-muted">Error loading lead data</p>';
                }
            }
            
            function refreshData() {
                if (currentBusinessId) {
                    const hotelName = document.getElementById('hotelName').textContent;
                    loadHotelData(currentBusinessId, hotelName);
                }
            }
            
            // Load default hotel on page load
            window.onload = function() {
                loadHotelData('aloha_resort_waikiki', 'Aloha Resort Waikiki');
            };
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=dashboard_html)