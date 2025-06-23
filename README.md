# Tourism Analytics Platform

A comprehensive FastAPI-based analytics platform for tourism businesses featuring visitor sentiment analysis, demand forecasting, multilingual chatbot, business insights dashboard, and HubSpot CRM integration.

## Features

### 🎯 Core Analytics Modules

1. **Visitor Sentiment Analysis**
   - Real-time sentiment analysis of customer reviews
   - Emotion detection and keyword extraction
   - Multi-language support
   - Trend analysis and insights

2. **Demand Forecasting**
   - Machine learning-based visitor demand prediction
   - Seasonal pattern analysis
   - Multiple forecasting models (Random Forest, Gradient Boosting, Linear Regression)
   - Confidence intervals and accuracy metrics

3. **Multilingual Chatbot**
   - AI-powered tourist inquiry handling
   - Intent classification and entity extraction
   - Multi-language support with automatic translation
   - Performance analytics and feedback system

4. **Business Insights Dashboard**
   - Interactive Plotly visualizations
   - Real-time metrics and KPIs
   - Customizable date ranges and filters
   - Export capabilities

5. **HubSpot CRM Integration**
   - Automated lead management
   - Bi-directional sync with HubSpot
   - Activity tracking and deal creation
   - Lead scoring and conversion tracking

## Technology Stack

- **Backend**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session management and caching
- **ML/AI**: scikit-learn, NLTK, TextBlob, Transformers, OpenAI
- **Visualization**: Plotly for interactive charts
- **Deployment**: Docker and Docker Compose
- **API Integration**: HubSpot API, Google Translate API, OpenAI API

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd tourism-analytics-platform
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up the database**
```bash
# Create database
createdb tourism_analytics

# Run migrations
alembic upgrade head
```

5. **Start Redis**
```bash
redis-server
```

6. **Run the application**
```bash
uvicorn main:app --reload
```

### Docker Setup

```bash
# Build and start all services
docker-compose up --build

# Run migrations
docker-compose exec app alembic upgrade head
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/tourism_analytics
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key

# External APIs
OPENAI_API_KEY=your-openai-api-key
HUBSPOT_API_KEY=your-hubspot-api-key
GOOGLE_TRANSLATE_API_KEY=your-google-translate-api-key
```

## Usage Examples

### 1. Add Review and Analyze Sentiment

```python
import httpx

# Add a review
review_data = {
    "business_id": "hotel_123",
    "reviewer_name": "John Doe",
    "rating": 4.5,
    "review_text": "Great hotel with excellent service!",
    "language": "en"
}

response = httpx.post("http://localhost:8000/api/v1/reviews/", json=review_data)
```

### 2. Generate Demand Forecast

```python
# Add historical data
tourism_data = {
    "business_id": "hotel_123",
    "date": "2024-01-15",
    "visitor_count": 150,
    "revenue": 15000.0,
    "bookings": 75
}

httpx.post("http://localhost:8000/api/v1/forecasting/data", json=tourism_data)

# Train models
httpx.post("http://localhost:8000/api/v1/forecasting/train?business_id=hotel_123")

# Generate forecast
forecast_request = {
    "business_id": "hotel_123",
    "days_ahead": 30
}

httpx.post("http://localhost:8000/api/v1/forecasting/forecast", json=forecast_request)
```

### 3. Chat with the Bot

```python
# Create chat session
session_data = {
    "business_id": "hotel_123",
    "language": "en"
}

session_response = httpx.post("http://localhost:8000/api/v1/chat/session", json=session_data)
session_id = session_response.json()["session_id"]

# Send message
message_data = {
    "session_id": session_id,
    "message": "I want to book a room for next weekend",
    "business_id": "hotel_123"
}

httpx.post("http://localhost:8000/api/v1/chat/message", json=message_data)
```

### 4. Create and Manage Leads

```python
# Create lead
lead_data = {
    "business_id": "hotel_123",
    "email": "customer@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "travel_dates": "2024-07-15 to 2024-07-20",
    "destination": "Paris",
    "party_size": 2
}

httpx.post("http://localhost:8000/api/v1/leads/", json=lead_data)
```

### 5. Get Dashboard Data

```python
# Get overview dashboard
response = httpx.get("http://localhost:8000/api/v1/dashboard/overview?business_id=hotel_123&days=30")
dashboard_data = response.json()
```

## API Endpoints

### Reviews
- `POST /api/v1/reviews/` - Create review
- `GET /api/v1/reviews/` - Get reviews with filters
- `GET /api/v1/reviews/analytics` - Get sentiment analytics
- `POST /api/v1/reviews/process-batch` - Process unprocessed reviews

### Forecasting
- `POST /api/v1/forecasting/data` - Add tourism data
- `POST /api/v1/forecasting/train` - Train models
- `POST /api/v1/forecasting/forecast` - Generate forecast
- `GET /api/v1/forecasting/accuracy` - Get accuracy metrics

### Chat
- `POST /api/v1/chat/session` - Create chat session
- `POST /api/v1/chat/message` - Send message
- `GET /api/v1/chat/analytics` - Get chat analytics
- `POST /api/v1/chat/feedback` - Add feedback

### Leads
- `POST /api/v1/leads/` - Create lead
- `GET /api/v1/leads/` - Get leads
- `PUT /api/v1/leads/{id}` - Update lead
- `POST /api/v1/leads/{id}/convert` - Convert lead
- `POST /api/v1/leads/sync/hubspot` - Sync to HubSpot

### Dashboard
- `GET /api/v1/dashboard/overview` - Overview dashboard
- `GET /api/v1/dashboard/sentiment` - Sentiment dashboard
- `GET /api/v1/dashboard/forecast` - Forecast dashboard
- `GET /api/v1/dashboard/chat` - Chat analytics dashboard

## Model Training

### Sentiment Analysis
The sentiment analysis uses pre-trained models from Hugging Face:
- `cardiffnlp/twitter-roberta-base-sentiment-latest` for sentiment
- `j-hartmann/emotion-english-distilroberta-base` for emotions

### Demand Forecasting
Multiple models are trained and compared:
- Random Forest Regressor
- Gradient Boosting Regressor
- Linear Regression

Models are automatically retrained when new data is added.

## Monitoring and Logging

- Health check endpoints: `/api/v1/health/`
- Detailed health check: `/api/v1/health/detailed`
- Built-in error handling and logging
- Performance metrics tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.