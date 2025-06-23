import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import httpx
import asyncio
from datetime import datetime, timedelta
import json

# Configure the page
st.set_page_config(
    page_title="Tourism Analytics Dashboard",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE = "http://localhost:8000/api/v1"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_data(endpoint, params=None):
    """Fetch data from API with caching"""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{API_BASE}{endpoint}", params=params or {})
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def create_sentiment_charts(business_id):
    """Create sentiment analysis charts"""
    
    # Get sentiment analytics
    sentiment_data = fetch_data("/reviews/analytics", {"business_id": business_id, "days": 30})
    
    if not sentiment_data or sentiment_data.get('status') != 'success':
        st.error("Failed to load sentiment data")
        return
    
    analytics = sentiment_data['analytics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Sentiment",
            value=analytics['overall_sentiment'].title(),
            delta=analytics['trend_analysis']['trend'].title()
        )
    
    with col2:
        st.metric(
            label="Average Score",
            value=f"{analytics['average_score']:.3f}",
            delta=f"{analytics['average_score']:.1%}" if analytics['average_score'] > 0 else None
        )
    
    with col3:
        st.metric(
            label="Total Reviews",
            value=analytics['total_reviews']
        )
    
    with col4:
        positive_pct = (analytics['sentiment_distribution']['positive'] / analytics['total_reviews'] * 100) if analytics['total_reviews'] > 0 else 0
        st.metric(
            label="Positive Reviews",
            value=f"{positive_pct:.1f}%"
        )
    
    # Sentiment Distribution Pie Chart
    col1, col2 = st.columns(2)
    
    with col1:
        if analytics.get('sentiment_distribution'):
            dist = analytics['sentiment_distribution']
            fig_pie = px.pie(
                values=list(dist.values()),
                names=list(dist.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'positive': '#2E8B57',
                    'neutral': '#FFD700', 
                    'negative': '#DC143C'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        if analytics.get('top_emotions'):
            emotions = analytics['top_emotions']
            fig_emotions = px.bar(
                x=list(emotions.keys()),
                y=list(emotions.values()),
                title="Top Emotions Detected",
                color=list(emotions.values()),
                color_continuous_scale="viridis"
            )
            fig_emotions.update_layout(showlegend=False)
            st.plotly_chart(fig_emotions, use_container_width=True)
    
    # Sentiment Trend Over Time
    if analytics.get('trend_analysis', {}).get('daily_scores'):
        trend_data = analytics['trend_analysis']['daily_scores']
        df_trend = pd.DataFrame(trend_data)
        df_trend['date'] = pd.to_datetime(df_trend['date'])
        
        fig_trend = px.line(
            df_trend,
            x='date',
            y='avg_sentiment',
            title="Sentiment Trend Over Time",
            markers=True
        )
        fig_trend.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        fig_trend.update_layout(yaxis_title="Average Sentiment Score")
        st.plotly_chart(fig_trend, use_container_width=True)

def create_forecasting_charts(business_id):
    """Create demand forecasting charts"""
    
    # Generate forecast
    forecast_data = fetch_data("/forecasting/forecast", {"business_id": business_id, "days_ahead": 14})
    
    if not forecast_data or forecast_data.get('status') != 'success':
        st.error("Failed to load forecast data")
        return
    
    predictions = forecast_data['predictions']
    df_forecast = pd.DataFrame(predictions)
    df_forecast['date'] = pd.to_datetime(df_forecast['date'])
    
    # Get historical data for comparison
    historical_data = fetch_data("/forecasting/data", {"business_id": business_id, "limit": 30})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_predicted = sum(p['predicted_visitors'] for p in predictions)
        st.metric(
            label="14-Day Forecast",
            value=f"{int(total_predicted):,} visitors"
        )
    
    with col2:
        avg_daily = total_predicted / len(predictions)
        st.metric(
            label="Daily Average",
            value=f"{int(avg_daily)} visitors"
        )
    
    with col3:
        if forecast_data.get('model_performance', {}).get('r2'):
            accuracy = forecast_data['model_performance']['r2'] * 100
            st.metric(
                label="Model Accuracy",
                value=f"{accuracy:.1f}%"
            )
    
    # Forecast Chart
    fig_forecast = go.Figure()
    
    # Add historical data if available
    if historical_data and historical_data.get('status') == 'success':
        hist_df = pd.DataFrame(historical_data['data'][-14:])  # Last 14 days
        hist_df['date'] = pd.to_datetime(hist_df['date'])
        
        fig_forecast.add_trace(go.Scatter(
            x=hist_df['date'],
            y=hist_df['visitor_count'],
            mode='lines+markers',
            name='Historical Data',
            line=dict(color='blue')
        ))
    
    # Add forecast
    fig_forecast.add_trace(go.Scatter(
        x=df_forecast['date'],
        y=df_forecast['predicted_visitors'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='orange', dash='dash')
    ))
    
    # Add confidence interval
    fig_forecast.add_trace(go.Scatter(
        x=df_forecast['date'],
        y=df_forecast['confidence_upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=df_forecast['date'],
        y=df_forecast['confidence_lower'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(255, 165, 0, 0.2)',
        line=dict(width=0),
        name='Confidence Interval',
        hoverinfo='skip'
    ))
    
    fig_forecast.update_layout(
        title="14-Day Visitor Demand Forecast",
        xaxis_title="Date",
        yaxis_title="Number of Visitors",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_forecast, use_container_width=True)

def create_chat_analytics_charts(business_id):
    """Create chat analytics charts"""
    
    chat_data = fetch_data("/chat/analytics", {"business_id": business_id})
    
    if not chat_data or chat_data.get('status') != 'success':
        st.warning("No chat data available")
        return
    
    analytics = chat_data['analytics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Sessions",
            value=analytics['total_sessions']
        )
    
    with col2:
        st.metric(
            label="Total Messages", 
            value=analytics['total_messages']
        )
    
    with col3:
        st.metric(
            label="Avg Response Time",
            value=f"{analytics['average_response_time_ms']:.0f}ms"
        )
    
    with col4:
        st.metric(
            label="User Rating",
            value=f"{analytics['average_rating']:.1f}/5.0"
        )
    
    # Intent Distribution
    if analytics.get('intent_distribution'):
        col1, col2 = st.columns(2)
        
        with col1:
            intents = analytics['intent_distribution']
            fig_intents = px.bar(
                x=list(intents.keys()),
                y=list(intents.values()),
                title="User Intent Distribution",
                color=list(intents.values()),
                color_continuous_scale="blues"
            )
            st.plotly_chart(fig_intents, use_container_width=True)
        
        with col2:
            if analytics.get('language_distribution'):
                languages = analytics['language_distribution']
                fig_lang = px.pie(
                    values=list(languages.values()),
                    names=list(languages.keys()),
                    title="Language Distribution"
                )
                st.plotly_chart(fig_lang, use_container_width=True)

def create_lead_analytics_charts(business_id):
    """Create lead management charts"""
    
    lead_data = fetch_data(f"/leads/analytics/{business_id}")
    
    if not lead_data or lead_data.get('status') != 'success':
        st.warning("No lead data available")
        return
    
    analytics = lead_data['analytics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Leads",
            value=analytics['total_leads']
        )
    
    with col2:
        st.metric(
            label="Converted Leads",
            value=analytics['converted_leads']
        )
    
    with col3:
        st.metric(
            label="Conversion Rate",
            value=f"{analytics['conversion_rate']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Total Value",
            value=f"${analytics['total_conversion_value']:,.0f}"
        )
    
    # Lead Status and Source Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        if analytics.get('status_distribution'):
            status_dist = analytics['status_distribution']
            fig_status = px.pie(
                values=list(status_dist.values()),
                names=list(status_dist.keys()),
                title="Lead Status Distribution"
            )
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        if analytics.get('source_distribution'):
            source_dist = analytics['source_distribution']
            fig_source = px.bar(
                x=list(source_dist.keys()),
                y=list(source_dist.values()),
                title="Lead Source Distribution",
                color=list(source_dist.values()),
                color_continuous_scale="greens"
            )
            st.plotly_chart(fig_source, use_container_width=True)

def main():
    st.title("🌺 Tourism Analytics Dashboard")
    st.markdown("Real-time insights for Hawaiian hotel operations")
    
    # Sidebar for hotel selection
    st.sidebar.title("Hotel Selection")
    
    hotels = {
        "Aloha Resort Waikiki": "aloha_resort_waikiki",
        "Maui Beach Hotel & Spa": "maui_beach_hotel",
        "Kona Village Resort": "kona_village_resort", 
        "Halekulani Luxury Hotel": "halekulani_luxury",
        "Napali Coast Inn": "napali_coast_inn"
    }
    
    selected_hotel = st.sidebar.selectbox(
        "Choose a hotel:",
        options=list(hotels.keys()),
        index=0
    )
    
    business_id = hotels[selected_hotel]
    
    st.sidebar.markdown(f"**Selected:** {selected_hotel}")
    
    # Dashboard sections
    dashboard_type = st.sidebar.radio(
        "Dashboard Type:",
        ["Overview", "Sentiment Analysis", "Demand Forecasting", "Chat Analytics", "Lead Management"]
    )
    
    # Auto-refresh
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Main dashboard content
    if dashboard_type == "Overview":
        st.header(f"📊 Overview Dashboard - {selected_hotel}")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Sentiment", "Forecasting", "Chat", "Leads"])
        
        with tab1:
            create_sentiment_charts(business_id)
        
        with tab2:
            create_forecasting_charts(business_id)
        
        with tab3:
            create_chat_analytics_charts(business_id)
        
        with tab4:
            create_lead_analytics_charts(business_id)
    
    elif dashboard_type == "Sentiment Analysis":
        st.header(f"💭 Sentiment Analysis - {selected_hotel}")
        create_sentiment_charts(business_id)
    
    elif dashboard_type == "Demand Forecasting":
        st.header(f"📈 Demand Forecasting - {selected_hotel}")
        create_forecasting_charts(business_id)
    
    elif dashboard_type == "Chat Analytics":
        st.header(f"💬 Chat Analytics - {selected_hotel}")
        create_chat_analytics_charts(business_id)
    
    elif dashboard_type == "Lead Management":
        st.header(f"👥 Lead Management - {selected_hotel}")
        create_lead_analytics_charts(business_id)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("🌺 **Tourism Analytics Platform**")
    st.sidebar.markdown("Powered by FastAPI, Streamlit & AI")
    
    # Health check in sidebar
    health_data = fetch_data("/health/")
    if health_data:
        st.sidebar.success("✅ System Healthy")
    else:
        st.sidebar.error("❌ System Issues")

if __name__ == "__main__":
    main()