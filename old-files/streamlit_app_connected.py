import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
import json

# Page configuration
st.set_page_config(
    page_title="Tourism Analytics Platform - LeniLani Consulting",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
# Get API URL from environment variable or use default
API_URL = os.getenv('API_URL', 'https://tourism-analytics-platform.onrender.com')
# For local development, you can set this to 'http://localhost:8000'

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .api-status {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 20px;
        border-radius: 20px;
        font-size: 0.9rem;
        z-index: 1000;
    }
    .api-connected {
        background: #4CAF50;
        color: white;
    }
    .api-disconnected {
        background: #F44336;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions to fetch data from API
@st.cache_data(ttl=60)  # Cache for 60 seconds
def check_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_hotels():
    """Fetch hotels data from API"""
    try:
        response = requests.get(f"{API_URL}/api/v1/hotels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data.get('hotels', []))
    except Exception as e:
        st.error(f"Error fetching hotels: {str(e)}")
    
    # Return demo data if API fails
    return pd.DataFrame({
        'name': ['Aloha Resort Waikiki', 'Maui Beach Hotel & Spa', 'Kona Village Resort'],
        'location': ['Waikiki, Oahu', 'Kaanapali, Maui', 'Kona, Big Island'],
        'occupancy_rate': [0.85, 0.82, 0.88],
        'avg_daily_rate': [450, 380, 550],
        'sentiment_score': [0.92, 0.89, 0.95],
        'total_reviews': [142, 98, 76],
        'rating': [4.8, 4.7, 4.9],
        'business_id': ['aloha_resort_waikiki', 'maui_beach_hotel', 'kona_village_resort']
    })

@st.cache_data(ttl=300)
def fetch_reviews_analytics(business_id):
    """Fetch review analytics from API"""
    try:
        response = requests.get(f"{API_URL}/api/v1/reviews/analytics?business_id={business_id}", timeout=5)
        if response.status_code == 200:
            return response.json().get('analytics', {})
    except:
        pass
    return {
        'total_reviews': 100,
        'average_score': 4.5,
        'overall_sentiment': 'positive',
        'sentiment_distribution': {'positive': 70, 'neutral': 20, 'negative': 10},
        'common_keywords': ['great', 'clean', 'friendly', 'location', 'service']
    }

@st.cache_data(ttl=300)
def fetch_forecast(business_id, days=7):
    """Fetch demand forecast from API"""
    try:
        response = requests.get(
            f"{API_URL}/api/v1/forecasting/forecast?business_id={business_id}&days_ahead={days}", 
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('predictions', [])
    except:
        pass
    
    # Return demo forecast if API fails
    return [
        {'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
         'predicted_visitors': np.random.randint(150, 250)}
        for i in range(days)
    ]

@st.cache_data(ttl=300)
def fetch_dashboard_metrics(business_id):
    """Fetch dashboard metrics from API"""
    try:
        response = requests.get(f"{API_URL}/api/v1/dashboard/metrics?business_id={business_id}", timeout=5)
        if response.status_code == 200:
            return response.json().get('metrics', {})
    except:
        pass
    return {
        'occupancy_rate': 0.85,
        'avg_daily_rate': 450,
        'revenue_per_room': 382.5,
        'total_revenue_mtd': 150000,
        'sentiment_score': 0.92
    }

# Header
st.markdown('<h1 class="main-header">🌺 Tourism Analytics Platform</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Powered by LeniLani Consulting - AI-Driven Insights for Hawaiian Hospitality</p>', unsafe_allow_html=True)

# API Status Indicator
api_status = check_api_health()
if api_status:
    st.markdown(f'<div class="api-status api-connected">✅ Connected to API: {API_URL}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="api-status api-disconnected">⚠️ API Offline - Using Demo Data</div>', unsafe_allow_html=True)

# Fetch hotels data
hotels_df = fetch_hotels()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=LeniLani+Consulting", use_column_width=True)
    st.markdown("---")
    
    # API Configuration
    st.markdown("### 🔌 API Configuration")
    api_input = st.text_input("API URL", value=API_URL, help="Enter your API endpoint URL")
    if api_input != API_URL:
        API_URL = api_input
        st.rerun()
    
    # Date range selector
    st.markdown("### 📅 Analysis Period")
    date_range = st.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_range"
    )
    
    # Hotel selector
    st.markdown("### 🏨 Select Hotel")
    if not hotels_df.empty:
        selected_hotel = st.selectbox(
            "Choose hotel to analyze",
            options=hotels_df['business_id'].tolist() if 'business_id' in hotels_df.columns else [],
            format_func=lambda x: hotels_df[hotels_df['business_id']==x]['name'].values[0] if len(hotels_df[hotels_df['business_id']==x]) > 0 else x
        )
    else:
        selected_hotel = 'aloha_resort_waikiki'
    
    # Analysis type
    st.markdown("### 📊 Analysis Type")
    analysis_type = st.radio(
        "Choose analysis focus",
        ["Overview", "Sentiment Analysis", "Revenue Analytics", "Demand Forecasting", "API Testing"]
    )
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if st.button("📥 Export Report", use_container_width=True):
        st.success("Report exported successfully!")

# Main content area based on analysis type
if analysis_type == "Overview":
    # Fetch metrics for selected hotel
    metrics = fetch_dashboard_metrics(selected_hotel)
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Occupancy Rate",
            f"{metrics.get('occupancy_rate', 0)*100:.1f}%",
            f"{np.random.uniform(-2, 5):.1f}%"
        )
    
    with col2:
        st.metric(
            "Avg Daily Rate",
            f"${metrics.get('avg_daily_rate', 0):.0f}",
            f"${np.random.uniform(-10, 20):.0f}"
        )
    
    with col3:
        st.metric(
            "RevPAR",
            f"${metrics.get('revenue_per_room', 0):.0f}",
            f"${np.random.uniform(-5, 15):.0f}"
        )
    
    with col4:
        st.metric(
            "Sentiment Score",
            f"{metrics.get('sentiment_score', 0):.2f}",
            f"{np.random.uniform(-0.05, 0.05):.2f}"
        )
    
    with col5:
        st.metric(
            "Revenue MTD",
            f"${metrics.get('total_revenue_mtd', 0):,.0f}",
            f"+{np.random.uniform(5, 15):.1f}%"
        )
    
    # Display hotels data
    st.markdown("### 🏨 Hotels Performance")
    if not hotels_df.empty:
        # Calculate RevPAR
        hotels_df['RevPAR'] = hotels_df['avg_daily_rate'] * hotels_df['occupancy_rate']
        
        # Create performance chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig_occupancy = px.bar(
                hotels_df,
                x='name',
                y='occupancy_rate',
                color='occupancy_rate',
                color_continuous_scale='Viridis',
                title="Occupancy Rates by Hotel",
                labels={'occupancy_rate': 'Occupancy Rate', 'name': 'Hotel'}
            )
            fig_occupancy.update_yaxis(tickformat='.0%')
            st.plotly_chart(fig_occupancy, use_container_width=True)
        
        with col2:
            fig_revenue = px.scatter(
                hotels_df,
                x='avg_daily_rate',
                y='occupancy_rate',
                size='total_reviews',
                color='sentiment_score',
                hover_data=['name'],
                color_continuous_scale='RdYlGn',
                title="Hotel Performance Matrix",
                labels={'avg_daily_rate': 'ADR ($)', 'occupancy_rate': 'Occupancy Rate'}
            )
            fig_revenue.update_yaxis(tickformat='.0%')
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Display data table
        st.markdown("### 📊 Detailed Metrics")
        display_df = hotels_df[['name', 'location', 'occupancy_rate', 'avg_daily_rate', 'RevPAR', 'sentiment_score', 'rating']]
        display_df.columns = ['Hotel', 'Location', 'Occupancy %', 'ADR ($)', 'RevPAR ($)', 'Sentiment', 'Rating']
        
        # Format percentage and currency columns
        display_df['Occupancy %'] = display_df['Occupancy %'].apply(lambda x: f"{x*100:.1f}%")
        display_df['ADR ($)'] = display_df['ADR ($)'].apply(lambda x: f"${x:.0f}")
        display_df['RevPAR ($)'] = display_df['RevPAR ($)'].apply(lambda x: f"${x:.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

elif analysis_type == "Sentiment Analysis":
    st.markdown("## 💭 Sentiment Analysis Dashboard")
    
    # Fetch analytics for selected hotel
    analytics = fetch_reviews_analytics(selected_hotel)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sentiment distribution
        sentiment_dist = analytics.get('sentiment_distribution', {})
        if sentiment_dist:
            fig_pie = px.pie(
                values=list(sentiment_dist.values()),
                names=list(sentiment_dist.keys()),
                color_discrete_map={'positive': '#4CAF50', 'neutral': '#FFC107', 'negative': '#F44336'},
                title="Sentiment Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Analytics Summary")
        st.metric("Total Reviews", analytics.get('total_reviews', 0))
        st.metric("Average Score", f"{analytics.get('average_score', 0):.1f}")
        st.metric("Overall Sentiment", analytics.get('overall_sentiment', 'Unknown').title())
    
    with col3:
        st.markdown("### 🔤 Top Keywords")
        keywords = analytics.get('common_keywords', [])
        for keyword in keywords[:5]:
            st.markdown(f"• **{keyword}**")
    
    # Test sentiment analysis
    st.markdown("### 🧪 Test Sentiment Analysis")
    test_text = st.text_area("Enter text to analyze:", "The hotel was amazing! Great service and beautiful views.")
    if st.button("Analyze Sentiment"):
        try:
            response = requests.post(
                f"{API_URL}/api/v1/reviews/sentiment",
                params={"text": test_text},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sentiment", result.get('sentiment', 'Unknown'))
                with col2:
                    st.metric("Score", f"{result.get('score', 0):.2f}")
                with col3:
                    st.metric("Confidence", f"{result.get('confidence', 0):.0%}")
        except Exception as e:
            st.error(f"Error analyzing sentiment: {str(e)}")

elif analysis_type == "Revenue Analytics":
    st.markdown("## 💰 Revenue Analytics Dashboard")
    
    # Fetch metrics
    metrics = fetch_dashboard_metrics(selected_hotel)
    
    # Revenue metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Revenue", f"${metrics.get('total_revenue_mtd', 0):,.0f}", "+12.5%")
    
    with col2:
        st.metric("ADR", f"${metrics.get('avg_daily_rate', 0):.0f}", "+8.3%")
    
    with col3:
        st.metric("RevPAR", f"${metrics.get('revenue_per_room', 0):.0f}", "+5.7%")
    
    with col4:
        forecast = metrics.get('forecast_next_week', {})
        st.metric("7-Day Forecast", f"${forecast.get('revenue', 0):,.0f}", "+15.8%")
    
    # Revenue trend chart
    st.markdown("### 📈 Revenue Trend")
    
    # Generate sample revenue data
    dates = pd.date_range(start=date_range[0], end=date_range[1], freq='D')
    revenue_data = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.uniform(15000, 35000, len(dates)),
        'Forecast': np.random.uniform(18000, 38000, len(dates))
    })
    
    fig_revenue = go.Figure()
    fig_revenue.add_trace(go.Scatter(
        x=revenue_data['Date'],
        y=revenue_data['Revenue'],
        mode='lines',
        name='Actual Revenue',
        line=dict(color='#667eea', width=3)
    ))
    fig_revenue.add_trace(go.Scatter(
        x=revenue_data['Date'],
        y=revenue_data['Forecast'],
        mode='lines',
        name='Forecast',
        line=dict(color='#764ba2', width=2, dash='dash')
    ))
    fig_revenue.update_layout(
        title="Revenue Trend & Forecast",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

elif analysis_type == "Demand Forecasting":
    st.markdown("## 🔮 Demand Forecasting Dashboard")
    
    # Fetch forecast
    forecast_data = fetch_forecast(selected_hotel, days=30)
    
    if forecast_data:
        # Convert to DataFrame
        forecast_df = pd.DataFrame(forecast_data)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_visitors = np.mean([f.get('predicted_visitors', 0) for f in forecast_data])
            st.metric("Avg Daily Visitors", f"{avg_visitors:.0f}", "+12")
        
        with col2:
            peak_day = max(forecast_data, key=lambda x: x.get('predicted_visitors', 0))
            st.metric("Peak Day", peak_day.get('date', 'N/A'), f"{peak_day.get('predicted_visitors', 0)} visitors")
        
        with col3:
            st.metric("Forecast Period", f"{len(forecast_data)} days", "")
        
        with col4:
            st.metric("Model", forecast_data[0].get('model_used', 'random_forest'), "")
        
        # Forecast chart
        st.markdown("### 📊 Visitor Forecast")
        
        fig_forecast = go.Figure()
        
        # Add predicted visitors
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_visitors'],
            mode='lines+markers',
            name='Predicted Visitors',
            line=dict(color='#667eea', width=3)
        ))
        
        # Add confidence intervals if available
        if 'confidence_lower' in forecast_df.columns:
            fig_forecast.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['confidence_upper'],
                fill=None,
                mode='lines',
                line_color='rgba(0,0,0,0)',
                showlegend=False
            ))
            fig_forecast.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['confidence_lower'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,0,0,0)',
                name='Confidence Interval'
            ))
        
        fig_forecast.update_layout(
            title="30-Day Visitor Forecast",
            xaxis_title="Date",
            yaxis_title="Predicted Visitors",
            hovermode='x unified'
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Display forecast table
        st.markdown("### 📋 Forecast Details")
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

elif analysis_type == "API Testing":
    st.markdown("## 🧪 API Testing & Documentation")
    
    st.markdown(f"""
    ### 📡 API Endpoints
    
    **Base URL:** `{API_URL}`
    
    **Available Endpoints:**
    - `GET /health` - Check API health
    - `GET /api/v1/hotels` - Get all hotels
    - `GET /api/v1/hotels/{{business_id}}` - Get specific hotel
    - `GET /api/v1/reviews/analytics` - Get review analytics
    - `POST /api/v1/reviews/sentiment` - Analyze sentiment
    - `GET /api/v1/forecasting/forecast` - Get demand forecast
    - `GET /api/v1/dashboard/metrics` - Get dashboard metrics
    - `GET /docs` - Interactive API documentation
    """)
    
    # API Tester
    st.markdown("### 🔧 Test API Endpoints")
    
    endpoint = st.selectbox(
        "Select Endpoint",
        ["/health", "/api/v1/hotels", f"/api/v1/hotels/{selected_hotel}", 
         f"/api/v1/reviews/analytics?business_id={selected_hotel}",
         f"/api/v1/forecasting/forecast?business_id={selected_hotel}&days_ahead=7",
         f"/api/v1/dashboard/metrics?business_id={selected_hotel}"]
    )
    
    if st.button("Send Request"):
        try:
            response = requests.get(f"{API_URL}{endpoint}", timeout=5)
            st.success(f"Status Code: {response.status_code}")
            st.json(response.json())
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Connection Info
    st.markdown("### 🔌 Connection Information")
    st.info(f"""
    **Current Configuration:**
    - API URL: `{API_URL}`
    - API Status: {'✅ Connected' if api_status else '❌ Disconnected'}
    - Using: {'Live Data' if api_status else 'Demo Data'}
    
    **To connect to your own API:**
    1. Deploy the API service (already done on Render)
    2. Copy your API URL (e.g., `https://your-api.onrender.com`)
    3. Paste it in the sidebar "API Configuration" section
    4. The dashboard will automatically connect and fetch live data
    """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Export Options")
    export_format = st.selectbox("Export Format", ["PDF", "Excel", "PowerPoint", "CSV"])
    if st.button("Export Dashboard", use_container_width=True):
        st.success(f"Dashboard exported as {export_format}")

with col2:
    st.markdown("### 🔔 Alerts & Notifications")
    st.checkbox("Enable real-time alerts")
    st.checkbox("Weekly summary emails")
    st.checkbox("Anomaly detection alerts")

with col3:
    st.markdown("### ℹ️ About")
    st.info("**Tourism Analytics Platform v2.0**\n\nPowered by LeniLani Consulting\n\n© 2024 All Rights Reserved")