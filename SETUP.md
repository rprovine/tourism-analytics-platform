# 🌺 Tourism Analytics Platform - Setup Guide

A comprehensive FastAPI-based analytics platform for tourism businesses featuring AI-powered sentiment analysis, demand forecasting, multilingual chatbot, and business intelligence dashboards.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd tourism-analytics-platform
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional for demo)
# OPENAI_API_KEY=your-openai-key
# HUBSPOT_API_KEY=your-hubspot-key
# GOOGLE_TRANSLATE_API_KEY=your-google-translate-key
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# In another terminal, run database migrations
docker-compose exec app alembic upgrade head

# Seed with Hawaiian hotel demo data
python seed_data.py
```

### 4. Access the Platform

- **🏠 Main Landing Page**: http://localhost:8000/
- **📊 Interactive Dashboard**: http://localhost:8000/api/v1/web-dashboard/
- **🌟 Advanced Dashboard**: http://localhost:8501 (run `python run_dashboard.py`)
- **📚 API Documentation**: http://localhost:8000/docs

## 🛠️ Manual Setup (Alternative)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install & Start Services

```bash
# Install PostgreSQL
brew install postgresql
brew services start postgresql
createdb tourism_analytics

# Install Redis
brew install redis
brew services start redis
```

### 3. Run the Application

```bash
# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn main:app --reload

# In another terminal, start Streamlit dashboard
streamlit run app/dashboard/web_dashboard.py
```

## 📊 Demo Data

### Quick Demo Setup
```bash
python quick_demo.py
```

### Full Hawaiian Hotels Dataset
```bash
python seed_data.py
```

This creates data for 5 Hawaiian hotels:
- 🏖️ Aloha Resort Waikiki
- 🌊 Maui Beach Hotel & Spa  
- 🌋 Kona Village Resort
- ✨ Halekulani Luxury Hotel
- 🏔️ Napali Coast Inn

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `OPENAI_API_KEY` | OpenAI API key for chatbot | No |
| `HUBSPOT_API_KEY` | HubSpot CRM integration | No |
| `GOOGLE_TRANSLATE_API_KEY` | Google Translate API | No |

### External API Setup (Optional)

1. **OpenAI** (for better chatbot responses):
   - Get API key from https://openai.com/api/
   - Add to `.env`: `OPENAI_API_KEY=your-key`

2. **HubSpot** (for CRM integration):
   - Get API key from HubSpot Developer Account
   - Add to `.env`: `HUBSPOT_API_KEY=your-key`

3. **Google Translate** (for multilingual support):
   - Enable Google Translate API in Google Cloud Console
   - Add to `.env`: `GOOGLE_TRANSLATE_API_KEY=your-key`

## 🏗️ Architecture

```
├── app/
│   ├── api/v1/endpoints/     # FastAPI route handlers
│   ├── analytics/            # ML models (sentiment, forecasting)
│   ├── chatbot/             # Multilingual chatbot engine
│   ├── dashboard/           # Business intelligence dashboards
│   ├── integrations/        # External API integrations (HubSpot)
│   ├── models/              # SQLAlchemy database models
│   ├── services/            # Business logic layer
│   └── core/                # Configuration and database
├── alembic/                 # Database migrations
├── templates/               # HTML templates
├── static/                  # Static files
└── docker-compose.yml       # Docker configuration
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/api/v1/health/detailed
```

### API Testing
Use the interactive documentation at http://localhost:8000/docs

### Test Specific Features
```bash
# Test sentiment analysis
curl "http://localhost:8000/api/v1/reviews/analytics?business_id=aloha_resort_waikiki"

# Test demand forecasting
curl -X POST "http://localhost:8000/api/v1/forecasting/forecast" \
  -H "Content-Type: application/json" \
  -d '{"business_id": "aloha_resort_waikiki", "days_ahead": 14}'
```

## 🚨 Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Database connection issues:**
```bash
brew services restart postgresql
```

**Docker issues:**
```bash
docker-compose down
docker-compose up --build
```

**Dependencies issues:**
```bash
pip install --upgrade -r requirements.txt
```

## 📈 Usage Examples

### Creating a Review
```python
import httpx

review_data = {
    "business_id": "aloha_resort_waikiki",
    "reviewer_name": "John Doe",
    "rating": 4.5,
    "review_text": "Amazing hotel with great ocean views!",
    "language": "en"
}

response = httpx.post("http://localhost:8000/api/v1/reviews/", json=review_data)
```

### Getting Forecast
```python
forecast_request = {
    "business_id": "aloha_resort_waikiki",
    "days_ahead": 30
}

response = httpx.post("http://localhost:8000/api/v1/forecasting/forecast", json=forecast_request)
```

### Chat with Bot
```python
# Create session
session_data = {"business_id": "aloha_resort_waikiki", "language": "en"}
session = httpx.post("http://localhost:8000/api/v1/chat/session", json=session_data)

# Send message
message_data = {
    "session_id": session.json()["session_id"],
    "message": "I want to book a room",
    "business_id": "aloha_resort_waikiki"
}
response = httpx.post("http://localhost:8000/api/v1/chat/message", json=message_data)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 Check the [API Documentation](http://localhost:8000/docs)
- 🔍 Use the [Health Check](http://localhost:8000/api/v1/health/) to diagnose issues
- 📊 Monitor the [System Dashboard](http://localhost:8000/api/v1/web-dashboard/)

## 🌟 Features

- ✅ Real-time sentiment analysis of customer reviews
- ✅ AI-powered demand forecasting with ML models
- ✅ Multilingual chatbot for customer inquiries  
- ✅ Lead management with CRM integration
- ✅ Interactive business intelligence dashboards
- ✅ RESTful API with comprehensive documentation
- ✅ Docker deployment with auto-scaling
- ✅ Real-time analytics and monitoring