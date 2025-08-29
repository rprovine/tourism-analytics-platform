import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
from io import BytesIO
import base64

# Utility functions for exports
def export_to_csv(dataframe, filename):
    """Convert DataFrame to CSV download link"""
    csv = dataframe.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">📥 Download CSV</a>'
    return href

def create_weather_data():
    """Generate weather impact data"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    weather_data = []
    for date in dates:
        temp = 75 + 10 * np.sin(2 * np.pi * date.dayofyear / 365) + np.random.normal(0, 3)
        rain_prob = 0.3 + 0.2 * np.sin(2 * np.pi * (date.dayofyear - 100) / 365)
        bookings = max(0, 100 + 50 * (temp - 70) / 10 - 30 * rain_prob + np.random.normal(0, 15))
        weather_data.append({
            'date': date,
            'temperature': round(temp, 1),
            'rain_probability': round(rain_prob, 2),
            'bookings': int(bookings),
            'season': 'High' if date.month in [12, 1, 2, 6, 7, 8] else 'Low'
        })
    return pd.DataFrame(weather_data)

def create_pricing_data():
    """Generate dynamic pricing data"""
    dates = pd.date_range(start='2024-01-01', periods=365)
    pricing_data = []
    for date in dates:
        base_price = 450
        seasonal_mult = 1.4 if date.month in [12, 1, 2, 6, 7, 8] else 1.0
        weekend_mult = 1.2 if date.weekday() >= 5 else 1.0
        demand_mult = 0.8 + 0.4 * np.random.random()
        
        current_price = base_price * seasonal_mult * weekend_mult * demand_mult
        optimal_price = current_price * (1 + 0.1 * np.random.random())
        
        pricing_data.append({
            'date': date,
            'current_price': round(current_price, 2),
            'optimal_price': round(optimal_price, 2),
            'occupancy': round(60 + 30 * demand_mult + np.random.normal(0, 5), 1),
            'revenue_potential': round((optimal_price - current_price) * 100, 2)
        })
    return pd.DataFrame(pricing_data)

# Page configuration
st.set_page_config(
    page_title="Tourism Analytics Platform - LeniLani Consulting",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mobile responsiveness CSS
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .metric-container {
            margin-bottom: 1rem;
        }
        
        /* Make charts more readable on mobile */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* Sidebar adjustments for mobile */
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
        
        /* Better button sizing for mobile */
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        /* Responsive columns */
        .row-widget.stColumns {
            gap: 0.5rem;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
    }
    
    /* Enhanced visual styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 15px 15px;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

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
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for demo data
if 'hotels_data' not in st.session_state:
    st.session_state.hotels_data = pd.DataFrame({
        'Hotel': ['Aloha Resort Waikiki', 'Maui Beach Hotel & Spa', 'Kona Village Resort', 
                  'Halekulani Luxury', 'Napali Coast Inn'],
        'Location': ['Waikiki, Oahu', 'Kaanapali, Maui', 'Kona, Big Island', 
                     'Waikiki, Oahu', 'Kauai'],
        'Occupancy Rate': [85, 82, 88, 91, 79],
        'ADR': [450, 380, 550, 650, 320],
        'RevPAR': [382.5, 311.6, 484, 591.5, 252.8],
        'Sentiment Score': [0.92, 0.89, 0.95, 0.96, 0.87],
        'Total Reviews': [142, 98, 76, 234, 89],
        'Rating': [4.8, 4.7, 4.9, 4.9, 4.6]
    })

# Header
st.markdown('<h1 class="main-header">🌺 Tourism Analytics Platform</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Powered by LeniLani Consulting - AI-Driven Insights for Hawaiian Hospitality</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center; 
                margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🌺 LeniLani Consulting</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9rem;">Tourism Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Date range selector
    st.markdown("### 📅 Analysis Period")
    date_range = st.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        key="date_range"
    )
    
    # Hotel selector
    st.markdown("### 🏨 Select Hotels")
    selected_hotels = st.multiselect(
        "Choose hotels to analyze",
        options=st.session_state.hotels_data['Hotel'].tolist(),
        default=st.session_state.hotels_data['Hotel'].tolist()[:3]
    )
    
    # Analysis type
    st.markdown("### 📊 Analysis Type")
    analysis_type = st.radio(
        "Choose analysis focus",
        ["Overview", "Chat Analytics", "Sentiment Analysis", "Lead Management", 
         "Revenue Analytics", "Demand Forecasting", "Chatbot Simulator", 
         "API Integration", "Competitive Analysis", "Export & Reports", 
         "Smart Alerts", "Weather Impact", "Dynamic Pricing", "Customer Journey",
         "Marketing Attribution", "Event Impact", "Activity Recommendations"]
    )
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    if st.button("📥 Export Report", use_container_width=True):
        st.success("Report exported successfully!")
    if st.button("📧 Email Insights", use_container_width=True):
        st.success("Insights sent to stakeholders!")

# Filter data based on selection
filtered_data = st.session_state.hotels_data[st.session_state.hotels_data['Hotel'].isin(selected_hotels)]

# Main content area based on analysis type
if analysis_type == "Overview":
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_occupancy = filtered_data['Occupancy Rate'].mean()
        st.metric(
            "Avg Occupancy",
            f"{avg_occupancy:.1f}%",
            f"{random.uniform(-2, 5):.1f}%"
        )
    
    with col2:
        avg_adr = filtered_data['ADR'].mean()
        st.metric(
            "Avg Daily Rate",
            f"${avg_adr:.0f}",
            f"${random.uniform(-10, 20):.0f}"
        )
    
    with col3:
        avg_revpar = filtered_data['RevPAR'].mean()
        st.metric(
            "RevPAR",
            f"${avg_revpar:.0f}",
            f"${random.uniform(-5, 15):.0f}"
        )
    
    with col4:
        avg_sentiment = filtered_data['Sentiment Score'].mean()
        st.metric(
            "Sentiment Score",
            f"{avg_sentiment:.2f}",
            f"{random.uniform(-0.05, 0.05):.2f}"
        )
    
    with col5:
        total_reviews = filtered_data['Total Reviews'].sum()
        st.metric(
            "Total Reviews",
            f"{total_reviews:,}",
            f"+{random.randint(10, 50)}"
        )
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Occupancy Rate by Hotel")
        fig_occupancy = px.bar(
            filtered_data,
            x='Hotel',
            y='Occupancy Rate',
            color='Occupancy Rate',
            color_continuous_scale='Viridis',
            title="Current Occupancy Rates"
        )
        fig_occupancy.update_layout(showlegend=False)
        st.plotly_chart(fig_occupancy, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Revenue Performance")
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=filtered_data['Hotel'],
            y=filtered_data['ADR'],
            mode='lines+markers',
            name='ADR',
            line=dict(color='#667eea', width=3)
        ))
        fig_revenue.add_trace(go.Scatter(
            x=filtered_data['Hotel'],
            y=filtered_data['RevPAR'],
            mode='lines+markers',
            name='RevPAR',
            line=dict(color='#764ba2', width=3)
        ))
        fig_revenue.update_layout(title="ADR vs RevPAR Comparison", hovermode='x unified')
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Performance Matrix
    st.markdown("### 🎯 Performance Matrix")
    
    # Create performance data
    performance_data = filtered_data[['Hotel', 'Occupancy Rate', 'ADR', 'RevPAR', 'Sentiment Score', 'Rating']]
    performance_data['Performance Score'] = (
        performance_data['Occupancy Rate'] / 100 * 0.25 +
        performance_data['ADR'] / 700 * 0.25 +
        performance_data['RevPAR'] / 600 * 0.25 +
        performance_data['Sentiment Score'] * 0.25
    ) * 100
    
    # Display dataframe without gradient (matplotlib not available)
    st.dataframe(
        performance_data,
        use_container_width=True,
        height=300,
        column_config={
            "Performance Score": st.column_config.ProgressColumn(
                "Performance Score",
                help="Overall performance metric",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
            "Occupancy Rate": st.column_config.NumberColumn(
                "Occupancy Rate",
                help="Current occupancy percentage",
                format="%d%%",
            ),
            "ADR": st.column_config.NumberColumn(
                "ADR",
                help="Average Daily Rate",
                format="$%d",
            ),
            "RevPAR": st.column_config.NumberColumn(
                "RevPAR",
                help="Revenue per Available Room",
                format="$%.1f",
            ),
            "Sentiment Score": st.column_config.ProgressColumn(
                "Sentiment Score",
                help="Guest sentiment rating",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "Rating": st.column_config.NumberColumn(
                "Rating",
                help="Guest rating out of 5",
                format="%.1f⭐",
            ),
        }
    )

elif analysis_type == "Sentiment Analysis":
    st.markdown("## 💭 Sentiment Analysis Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sentiment distribution pie chart
        sentiment_dist = pd.DataFrame({
            'Sentiment': ['Positive', 'Neutral', 'Negative'],
            'Count': [random.randint(60, 80), random.randint(15, 25), random.randint(5, 15)]
        })
        fig_pie = px.pie(
            sentiment_dist,
            values='Count',
            names='Sentiment',
            color_discrete_map={'Positive': '#4CAF50', 'Neutral': '#FFC107', 'Negative': '#F44336'},
            title="Overall Sentiment Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Sentiment trend over time
        dates = pd.date_range(start=date_range[0], end=date_range[1], periods=30)
        sentiment_trend = pd.DataFrame({
            'Date': dates,
            'Sentiment Score': np.random.uniform(0.7, 0.95, 30)
        })
        fig_trend = px.line(
            sentiment_trend,
            x='Date',
            y='Sentiment Score',
            title="Sentiment Trend Over Time",
            line_shape='spline'
        )
        fig_trend.update_traces(line_color='#667eea')
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col3:
        # Top keywords
        st.markdown("### 🔤 Top Keywords")
        keywords = ['Beautiful', 'Clean', 'Friendly', 'Location', 'Service', 
                   'Pool', 'Beach', 'Breakfast', 'Comfortable', 'Value']
        counts = [random.randint(20, 100) for _ in keywords]
        
        for keyword, count in zip(keywords[:5], counts[:5]):
            st.markdown(f"**{keyword}**: {count} mentions")
    
    # Recent reviews analysis
    st.markdown("### 📝 Recent Review Analysis")
    
    reviews_data = pd.DataFrame({
        'Date': pd.date_range(start=datetime.now() - timedelta(days=5), periods=5),
        'Hotel': random.choices(selected_hotels, k=5),
        'Review': [
            "Amazing stay! The staff was incredibly friendly and helpful.",
            "Beautiful views and excellent service. Highly recommend!",
            "The room was clean and spacious. Great location near the beach.",
            "Loved the pool area and the breakfast was fantastic.",
            "Perfect for our honeymoon. Romantic setting and great amenities."
        ],
        'Sentiment': ['Positive', 'Positive', 'Positive', 'Positive', 'Positive'],
        'Score': [0.92, 0.89, 0.85, 0.91, 0.95]
    })
    
    st.dataframe(reviews_data, use_container_width=True)

elif analysis_type == "Revenue Analytics":
    st.markdown("## 💰 Revenue Analytics Dashboard")
    
    # Revenue metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        monthly_revenue = sum(filtered_data['ADR'] * filtered_data['Occupancy Rate'] / 100 * 30 * 100)
        st.metric("Monthly Revenue", f"${monthly_revenue:,.0f}", "+12.5%")
    
    with col2:
        avg_booking_value = filtered_data['ADR'].mean() * 3.5
        st.metric("Avg Booking Value", f"${avg_booking_value:.0f}", "+8.3%")
    
    with col3:
        revenue_per_room = filtered_data['RevPAR'].mean()
        st.metric("Revenue per Room", f"${revenue_per_room:.0f}", "+5.7%")
    
    with col4:
        yoy_growth = 15.8
        st.metric("YoY Growth", f"{yoy_growth}%", "+2.3%")
    
    # Revenue charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly revenue trend
        months = pd.date_range(start='2024-01', periods=12, freq='M')
        monthly_data = pd.DataFrame({
            'Month': months,
            'Revenue': np.random.uniform(800000, 1200000, 12),
            'Last Year': np.random.uniform(700000, 1000000, 12)
        })
        
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(x=monthly_data['Month'], y=monthly_data['Revenue'], 
                                     name='This Year', marker_color='#667eea'))
        fig_monthly.add_trace(go.Bar(x=monthly_data['Month'], y=monthly_data['Last Year'], 
                                     name='Last Year', marker_color='#764ba2'))
        fig_monthly.update_layout(title="Monthly Revenue Comparison", barmode='group')
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Revenue by source
        sources = pd.DataFrame({
            'Source': ['Direct Booking', 'OTA', 'Corporate', 'Group', 'Walk-in'],
            'Revenue': [35, 30, 20, 10, 5]
        })
        fig_sources = px.pie(sources, values='Revenue', names='Source', 
                            title="Revenue by Booking Source")
        st.plotly_chart(fig_sources, use_container_width=True)
    
    # Revenue forecast
    st.markdown("### 📈 Revenue Forecast")
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=90, freq='D')
    forecast_data = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted Revenue': np.random.uniform(25000, 45000, 90),
        'Lower Bound': np.random.uniform(20000, 40000, 90),
        'Upper Bound': np.random.uniform(30000, 50000, 90)
    })
    
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=forecast_data['Date'], y=forecast_data['Predicted Revenue'],
                                      mode='lines', name='Predicted', line=dict(color='#667eea', width=3)))
    fig_forecast.add_trace(go.Scatter(x=forecast_data['Date'], y=forecast_data['Upper Bound'],
                                      fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False))
    fig_forecast.add_trace(go.Scatter(x=forecast_data['Date'], y=forecast_data['Lower Bound'],
                                      fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)',
                                      name='Confidence Interval'))
    fig_forecast.update_layout(title="90-Day Revenue Forecast", hovermode='x unified')
    st.plotly_chart(fig_forecast, use_container_width=True)

elif analysis_type == "Demand Forecasting":
    st.markdown("## 🔮 Demand Forecasting Dashboard")
    
    # Forecasting metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        predicted_occupancy = 87.3
        st.metric("Next Week Occupancy", f"{predicted_occupancy}%", "+3.2%")
    
    with col2:
        predicted_bookings = 1247
        st.metric("Expected Bookings", f"{predicted_bookings:,}", "+156")
    
    with col3:
        peak_day = "Saturday"
        st.metric("Peak Day", peak_day, "")
    
    with col4:
        model_accuracy = 92.7
        st.metric("Model Accuracy", f"{model_accuracy}%", "+1.3%")
    
    # Demand forecast chart
    st.markdown("### 📊 30-Day Demand Forecast")
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    occupancy_forecast = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted Occupancy': np.random.uniform(75, 95, 30),
        'Actual (Historical)': np.random.uniform(70, 90, 30)
    })
    
    fig_demand = go.Figure()
    fig_demand.add_trace(go.Scatter(x=occupancy_forecast['Date'], 
                                    y=occupancy_forecast['Predicted Occupancy'],
                                    mode='lines+markers', name='Predicted',
                                    line=dict(color='#667eea', width=3)))
    fig_demand.add_trace(go.Scatter(x=occupancy_forecast['Date'], 
                                    y=occupancy_forecast['Actual (Historical)'],
                                    mode='lines+markers', name='Historical Average',
                                    line=dict(color='#764ba2', width=2, dash='dash')))
    fig_demand.update_layout(title="Occupancy Rate Forecast", yaxis_title="Occupancy %",
                             hovermode='x unified')
    st.plotly_chart(fig_demand, use_container_width=True)
    
    # Seasonal patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌊 Seasonal Patterns")
        seasons = pd.DataFrame({
            'Season': ['Winter', 'Spring', 'Summer', 'Fall'],
            'Avg Occupancy': [88, 82, 95, 78],
            'Avg ADR': [480, 420, 550, 380]
        })
        fig_seasonal = px.bar(seasons, x='Season', y=['Avg Occupancy', 'Avg ADR'],
                              title="Seasonal Performance Patterns", barmode='group')
        st.plotly_chart(fig_seasonal, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Day of Week Analysis")
        dow = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Occupancy': [72, 74, 78, 82, 91, 95, 93]
        })
        fig_dow = px.line(dow, x='Day', y='Occupancy', markers=True,
                         title="Occupancy by Day of Week")
        fig_dow.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig_dow, use_container_width=True)
    
    # Booking lead time analysis
    st.markdown("### ⏱️ Booking Lead Time Analysis")
    
    lead_time_data = pd.DataFrame({
        'Days in Advance': ['0-7', '8-14', '15-30', '31-60', '60+'],
        'Bookings': [15, 25, 35, 20, 5],
        'Avg Rate': [380, 420, 450, 430, 400]
    })
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(lead_time_data, use_container_width=True)
    with col2:
        fig_lead = px.pie(lead_time_data, values='Bookings', names='Days in Advance',
                         title="Booking Distribution by Lead Time")
        st.plotly_chart(fig_lead, use_container_width=True)

elif analysis_type == "Chat Analytics":
    st.markdown("## 💬 Chat Analytics Dashboard")
    
    # Chat metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Conversations", "2,847", "+312")
    
    with col2:
        st.metric("Avg Response Time", "1.2s", "-0.3s")
    
    with col3:
        st.metric("Resolution Rate", "94%", "+2%")
    
    with col4:
        st.metric("Satisfaction Score", "4.8/5", "+0.2")
    
    # Chat volume over time
    st.markdown("### 📊 Chat Volume Trends")
    dates = pd.date_range(start=date_range[0], end=date_range[1], freq='D')
    chat_volume = pd.DataFrame({
        'Date': dates,
        'Chats': np.random.randint(50, 150, len(dates)),
        'Unique Users': np.random.randint(30, 100, len(dates))
    })
    
    fig_chat = px.line(chat_volume, x='Date', y=['Chats', 'Unique Users'],
                       title="Daily Chat Activity")
    st.plotly_chart(fig_chat, use_container_width=True)
    
    # Intent analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Top Chat Intents")
        intents = pd.DataFrame({
            'Intent': ['Booking Inquiry', 'Room Service', 'Check-in/out', 'Amenities', 'Complaints'],
            'Count': [450, 380, 320, 280, 150]
        })
        fig_intents = px.pie(intents, values='Count', names='Intent',
                            title="Intent Distribution")
        st.plotly_chart(fig_intents, use_container_width=True)
    
    with col2:
        st.markdown("### 🌍 Language Distribution")
        languages = pd.DataFrame({
            'Language': ['English', 'Japanese', 'Chinese', 'Korean', 'Spanish'],
            'Percentage': [45, 25, 15, 10, 5]
        })
        fig_lang = px.bar(languages, x='Language', y='Percentage',
                         title="Chat Languages")
        st.plotly_chart(fig_lang, use_container_width=True)
    
    # Chat simulator
    st.markdown("### 🤖 Test Chatbot")
    user_message = st.text_input("Type a message to test the chatbot:")
    if user_message:
        with st.chat_message("user"):
            st.write(user_message)
        with st.chat_message("assistant"):
            responses = [
                "Thank you for your message! I'd be happy to help you with that.",
                "I understand your inquiry. Let me find that information for you.",
                "Great question! Here's what I can tell you about our services..."
            ]
            st.write(random.choice(responses))

elif analysis_type == "Lead Management":
    st.markdown("## 👥 Lead Management System")
    
    # Lead metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", "1,234", "+89")
    
    with col2:
        st.metric("Conversion Rate", "23.5%", "+3.2%")
    
    with col3:
        st.metric("Avg Lead Value", "$2,450", "+$120")
    
    with col4:
        st.metric("Pipeline Value", "$3.2M", "+$450K")
    
    # Lead funnel
    st.markdown("### 🔄 Lead Funnel")
    funnel_data = pd.DataFrame({
        'Stage': ['Awareness', 'Interest', 'Consideration', 'Intent', 'Purchase'],
        'Count': [5000, 2500, 1200, 600, 290]
    })
    
    fig_funnel = px.funnel(funnel_data, x='Count', y='Stage',
                          title="Lead Conversion Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Lead sources
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📍 Lead Sources")
        sources = pd.DataFrame({
            'Source': ['Website', 'Social Media', 'Email', 'Referral', 'Direct'],
            'Leads': [400, 350, 250, 180, 54]
        })
        fig_sources = px.pie(sources, values='Leads', names='Source')
        st.plotly_chart(fig_sources, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Lead Quality Score")
        quality_data = pd.DataFrame({
            'Score Range': ['90-100', '70-89', '50-69', '30-49', '0-29'],
            'Count': [150, 400, 350, 250, 84]
        })
        fig_quality = px.bar(quality_data, x='Score Range', y='Count',
                           color='Count', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_quality, use_container_width=True)
    
    # Lead details view
    st.markdown("### 📋 Recent Prospects")
    
    # Initialize prospect data with error handling
    try:
        # Sample prospect data
        prospects_data = {
            'Name': ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Lisa Park', 'Tom Wilson'],
            'Email': ['john@email.com', 'sarah@email.com', 'mike@email.com', 'lisa@email.com', 'tom@email.com'],
            'Source': ['Website', 'Social Media', 'Referral', 'Email', 'Direct'],
            'Score': [95, 87, 72, 68, 45],
            'Status': ['🔥 Hot', '🔥 Hot', '☀️ Warm', '☀️ Warm', '❄️ Cold'],
            'Last Contact': ['2 hours ago', '5 hours ago', '1 day ago', '2 days ago', '3 days ago']
        }
        
        # Create DataFrame with error handling
        prospects = pd.DataFrame(prospects_data)
        
        # Display the dataframe
        st.dataframe(prospects, use_container_width=True, height=250)
        
    except ImportError as e:
        st.error(f"Missing required library: {str(e)}")
        st.info("Please ensure all required packages are installed")
        
    except Exception as e:
        # Comprehensive fallback display
        st.warning(f"Table display issue: {str(e)}. Showing simplified view:")
        
        # Manual display without DataFrame
        prospects_list = [
            {"name": "John Smith", "email": "john@email.com", "status": "🔥 Hot", "score": 95},
            {"name": "Sarah Johnson", "email": "sarah@email.com", "status": "🔥 Hot", "score": 87},
            {"name": "Mike Chen", "email": "mike@email.com", "status": "☀️ Warm", "score": 72},
            {"name": "Lisa Park", "email": "lisa@email.com", "status": "☀️ Warm", "score": 68},
            {"name": "Tom Wilson", "email": "tom@email.com", "status": "❄️ Cold", "score": 45}
        ]
        
        for prospect in prospects_list:
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            with col1:
                st.write(f"**{prospect['name']}**")
            with col2:
                st.write(prospect['email'])
            with col3:
                st.write(prospect['status'])
            with col4:
                st.write(f"Score: {prospect['score']}")
            st.divider()
    
    # Lead capture form
    st.markdown("### ➕ Add New Lead")
    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        with col2:
            source = st.selectbox("Source", ['Website', 'Social Media', 'Email', 'Referral'])
            interest = st.selectbox("Interest Level", ['Hot', 'Warm', 'Cold'])
            notes = st.text_area("Notes")
        
        if st.form_submit_button("Add Lead"):
            if name and email:
                st.success(f"✅ Lead '{name}' added successfully!")
            else:
                st.error("Please fill in at least Name and Email fields")

elif analysis_type == "Chatbot Simulator":
    st.markdown("## 🤖 Interactive Chatbot Simulator")
    
    # Chatbot settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        language = st.selectbox("Language", ['English', 'Japanese', 'Chinese', 'Spanish'])
    
    with col2:
        personality = st.selectbox("Bot Personality", ['Professional', 'Friendly', 'Casual'])
    
    with col3:
        response_speed = st.slider("Response Speed (ms)", 100, 2000, 500)
    
    st.markdown("---")
    
    # Chat interface
    st.markdown("### 💬 Chat Interface")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🌺 Aloha! Welcome to our hotel. How can I assist you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate bot response
        responses = {
            "booking": "I'd be happy to help you with a booking! We have rooms available starting at $450/night. What dates are you interested in?",
            "amenities": "Our resort offers: 🏊 3 pools, 🏖️ Private beach access, 🍽️ 5 restaurants, 💆 Full-service spa, 🏋️ Fitness center, and 🎾 Tennis courts.",
            "check": "Check-in is at 3:00 PM and check-out is at 11:00 AM. Early check-in and late check-out may be available upon request.",
            "restaurant": "We have 5 dining options: 🍣 Sakura (Japanese), 🥩 The Grill (Steakhouse), 🌮 Sunset Cantina (Mexican), 🍕 Oceanview Bistro (Italian), and ☕ Aloha Café (Casual).",
            "default": "Thank you for your inquiry! I'm here to help make your stay memorable. Could you please provide more details about what you'd like to know?"
        }
        
        # Simple intent detection
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['book', 'reservation', 'available']):
            response = responses['booking']
        elif any(word in prompt_lower for word in ['amenity', 'facility', 'pool', 'gym']):
            response = responses['amenities']
        elif any(word in prompt_lower for word in ['check-in', 'checkout', 'time']):
            response = responses['check']
        elif any(word in prompt_lower for word in ['restaurant', 'food', 'dining', 'eat']):
            response = responses['restaurant']
        else:
            response = responses['default']
        
        # Add bot response
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Chat analytics
    st.markdown("### 📊 Current Session Analytics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Messages", len(st.session_state.messages))
    
    with col2:
        user_messages = len([m for m in st.session_state.messages if m['role'] == 'user'])
        st.metric("User Messages", user_messages)
    
    with col3:
        st.metric("Avg Response Time", f"{response_speed}ms")
    
    with col4:
        st.metric("Session Duration", "Active")

elif analysis_type == "API Integration":
    st.markdown("## 🔌 API Integration & Testing")
    
    # API endpoint tester
    st.markdown("### 🧪 API Endpoint Tester")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_method = st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"])
        api_endpoint = st.text_input("Endpoint", "/api/v1/hotels")
    
    with col2:
        api_params = st.text_area("Parameters (JSON)", '{"business_id": "aloha_resort_waikiki"}')
    
    if st.button("Send Request", type="primary"):
        st.markdown("#### Response")
        st.json({
            "status": "success",
            "data": {
                "hotel": "Aloha Resort Waikiki",
                "occupancy": 0.85,
                "adr": 450,
                "sentiment": 0.92
            },
            "timestamp": datetime.now().isoformat()
        })
    
    # API documentation
    st.markdown("### 📚 API Documentation")
    
    with st.expander("Hotels API"):
        st.code("""
        GET /api/v1/hotels - Get all hotels
        GET /api/v1/hotels/{id} - Get specific hotel
        POST /api/v1/hotels - Create new hotel
        PUT /api/v1/hotels/{id} - Update hotel
        DELETE /api/v1/hotels/{id} - Delete hotel
        """, language="http")
    
    with st.expander("Reviews API"):
        st.code("""
        GET /api/v1/reviews - Get all reviews
        GET /api/v1/reviews/sentiment - Analyze sentiment
        POST /api/v1/reviews - Add review
        GET /api/v1/reviews/analytics - Get analytics
        """, language="http")
    
    with st.expander("Chat API"):
        st.code("""
        POST /api/v1/chat/message - Send message
        GET /api/v1/chat/history - Get chat history
        GET /api/v1/chat/analytics - Get chat analytics
        POST /api/v1/chat/intent - Classify intent
        """, language="http")
    
    # API key management
    st.markdown("### 🔑 API Key Management")
    
    api_keys = pd.DataFrame({
        'Name': ['Production', 'Staging', 'Development'],
        'Key': ['pk_live_***', 'pk_test_***', 'pk_dev_***'],
        'Created': ['2024-01-15', '2024-02-20', '2024-03-10'],
        'Status': ['Active', 'Active', 'Inactive']
    })
    
    st.dataframe(api_keys, use_container_width=True)
    
    if st.button("Generate New API Key"):
        st.success("✅ New API key generated: pk_test_" + ''.join(random.choices('abcdef0123456789', k=16)))

elif analysis_type == "Competitive Analysis":
    st.markdown("## 🏆 Competitive Analysis Dashboard")
    
    # Market position
    st.markdown("### 📊 Market Position")
    
    market_data = pd.DataFrame({
        'Hotel': st.session_state.hotels_data['Hotel'],
        'Market Share': [22, 18, 25, 20, 15],
        'Price Index': [105, 95, 120, 140, 85],
        'Service Score': [4.8, 4.7, 4.9, 4.9, 4.6],
        'Online Rating': [4.8, 4.7, 4.9, 4.9, 4.6]
    })
    
    # Competitive positioning chart
    fig_position = px.scatter(market_data, x='Price Index', y='Service Score', 
                              size='Market Share', color='Hotel',
                              title="Competitive Positioning Matrix",
                              labels={'Price Index': 'Price Index (100 = Market Average)',
                                     'Service Score': 'Service Score (out of 5)'})
    fig_position.add_hline(y=4.75, line_dash="dash", line_color="gray")
    fig_position.add_vline(x=100, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_position, use_container_width=True)
    
    # Performance comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Performance Metrics Comparison")
        comparison_metrics = ['Occupancy Rate', 'ADR', 'RevPAR', 'Sentiment Score']
        
        fig_comparison = go.Figure()
        for hotel in selected_hotels[:3]:
            hotel_data = st.session_state.hotels_data[st.session_state.hotels_data['Hotel'] == hotel]
            values = [
                hotel_data['Occupancy Rate'].values[0] / 100,
                hotel_data['ADR'].values[0] / 700,
                hotel_data['RevPAR'].values[0] / 600,
                hotel_data['Sentiment Score'].values[0]
            ]
            fig_comparison.add_trace(go.Scatterpolar(
                r=values,
                theta=comparison_metrics,
                fill='toself',
                name=hotel
            ))
        fig_comparison.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                                    title="Competitive Performance Radar")
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Pricing Strategy Analysis")
        
        # Price comparison
        price_data = st.session_state.hotels_data[['Hotel', 'ADR']].copy()
        price_data['Market Avg'] = price_data['ADR'].mean()
        price_data['Difference'] = price_data['ADR'] - price_data['Market Avg']
        
        fig_price = px.bar(price_data, x='Hotel', y='Difference',
                          color='Difference', color_continuous_scale='RdYlGn',
                          title="Price Position vs Market Average")
        st.plotly_chart(fig_price, use_container_width=True)
    
    # SWOT Analysis
    st.markdown("### 🎯 Strategic Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**💪 Strengths**")
        st.info("• Prime locations\n• High service scores\n• Strong brand recognition")
    
    with col2:
        st.markdown("**⚠️ Weaknesses**")
        st.warning("• Higher price point\n• Limited inventory\n• Seasonal dependency")
    
    with col3:
        st.markdown("**🚀 Opportunities**")
        st.success("• Market expansion\n• Digital marketing\n• Package deals")
    
    with col4:
        st.markdown("**🔴 Threats**")
        st.error("• New competitors\n• Economic uncertainty\n• Travel restrictions")

elif analysis_type == "Export & Reports":
    st.markdown("## 📥 Export & Reporting System")
    
    # Report generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Generate Reports")
        report_type = st.selectbox("Report Type", [
            "Executive Summary", "Detailed Analytics", "Lead Report", 
            "Revenue Analysis", "Sentiment Report", "Custom Report"
        ])
        
        date_range = st.date_input(
            "Report Period",
            value=[datetime.now() - timedelta(days=30), datetime.now()],
            max_value=datetime.now()
        )
        
        format_type = st.radio("Export Format", ["PDF", "Excel", "PowerPoint", "CSV", "JSON"])
        
        if st.button("🎯 Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                # Simulate report generation
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                st.success(f"✅ {report_type} generated successfully!")
                st.download_button(
                    label=f"📥 Download {report_type}.{format_type.lower()}",
                    data="Sample report data...",
                    file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.{format_type.lower()}",
                    mime="application/octet-stream"
                )
    
    with col2:
        st.markdown("### 📧 Scheduled Reports")
        st.checkbox("📈 Daily KPI Summary")
        st.checkbox("📊 Weekly Performance Report") 
        st.checkbox("📉 Monthly Trend Analysis")
        st.checkbox("🎯 Quarterly Business Review")
        
        st.markdown("### 👥 Distribution List")
        recipients = st.text_area("Email Recipients", "management@lenilani.com\nanalytics@lenilani.com")
        
        if st.button("💾 Save Schedule"):
            st.success("Report schedule saved!")
    
    # Data export section
    st.markdown("### 📤 Raw Data Export")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics Data"):
            sample_data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=100),
                'Visitors': np.random.randint(100, 500, 100),
                'Revenue': np.random.randint(1000, 5000, 100)
            })
            st.markdown(export_to_csv(sample_data, "analytics_data"), unsafe_allow_html=True)
    
    with col2:
        if st.button("👥 Export Leads Data"):
            leads_data = pd.DataFrame({
                'Name': [f'Customer {i}' for i in range(50)],
                'Email': [f'customer{i}@email.com' for i in range(50)],
                'Score': np.random.randint(20, 100, 50)
            })
            st.markdown(export_to_csv(leads_data, "leads_data"), unsafe_allow_html=True)
    
    with col3:
        if st.button("💰 Export Revenue Data"):
            revenue_data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=365),
                'Revenue': np.random.randint(5000, 15000, 365),
                'Bookings': np.random.randint(50, 200, 365)
            })
            st.markdown(export_to_csv(revenue_data, "revenue_data"), unsafe_allow_html=True)

elif analysis_type == "Smart Alerts":
    st.markdown("## 🔔 Smart Alerts & Notification System")
    
    # Alert configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Alert Configuration")
        
        # Sentiment alerts
        st.markdown("**🎭 Sentiment Alerts**")
        sentiment_threshold = st.slider("Negative Sentiment Threshold (%)", 0, 100, 25)
        st.checkbox("📧 Email alerts for sentiment drops")
        st.checkbox("📱 SMS alerts for critical sentiment")
        
        # Revenue alerts  
        st.markdown("**💰 Revenue Alerts**")
        revenue_threshold = st.number_input("Daily Revenue Target ($)", value=10000)
        st.checkbox("🎯 Alert when target missed")
        st.checkbox("📈 Alert on revenue spikes")
        
        # Lead alerts
        st.markdown("**👥 Lead Alerts**")
        lead_threshold = st.slider("High-Value Lead Score", 50, 100, 80)
        st.checkbox("⭐ Instant alerts for high-value leads")
        
    with col2:
        st.markdown("### 🚨 Active Alerts")
        
        # Sample active alerts
        alerts = [
            {"type": "warning", "message": "Sentiment dropped 15% in last 24h", "time": "2 hours ago"},
            {"type": "success", "message": "Revenue target exceeded by 25%", "time": "4 hours ago"}, 
            {"type": "info", "message": "New high-value lead: John Smith (Score: 95)", "time": "6 hours ago"},
            {"type": "error", "message": "Booking cancellation spike detected", "time": "8 hours ago"}
        ]
        
        for alert in alerts:
            if alert['type'] == 'warning':
                st.warning(f"⚠️ {alert['message']} - {alert['time']}")
            elif alert['type'] == 'success':
                st.success(f"✅ {alert['message']} - {alert['time']}")
            elif alert['type'] == 'info':
                st.info(f"ℹ️ {alert['message']} - {alert['time']}")
            else:
                st.error(f"🚨 {alert['message']} - {alert['time']}")
    
    # Alert history
    st.markdown("### 📊 Alert Analytics")
    
    # Alert frequency chart
    alert_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30),
        'Critical': np.random.poisson(2, 30),
        'Warning': np.random.poisson(5, 30),
        'Info': np.random.poisson(8, 30)
    })
    
    fig_alerts = px.line(alert_data, x='Date', y=['Critical', 'Warning', 'Info'],
                        title="Alert Frequency Over Time")
    st.plotly_chart(fig_alerts, use_container_width=True)

elif analysis_type == "Weather Impact":
    st.markdown("## 🌦️ Weather Impact Analytics")
    
    # Generate weather data
    weather_df = create_weather_data()
    
    # Weather metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_temp = weather_df['temperature'].mean()
        st.metric("Average Temperature", f"{avg_temp:.1f}°F")
    
    with col2:
        avg_rain = weather_df['rain_probability'].mean()
        st.metric("Average Rain Probability", f"{avg_rain:.1%}")
    
    with col3:
        weather_corr = weather_df[['temperature', 'bookings']].corr().iloc[0,1]
        st.metric("Temp-Booking Correlation", f"{weather_corr:.3f}")
    
    with col4:
        rain_impact = -weather_df[['rain_probability', 'bookings']].corr().iloc[0,1]
        st.metric("Rain Impact Factor", f"{rain_impact:.3f}")
    
    # Weather impact visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌡️ Temperature vs Bookings")
        fig_temp = px.scatter(weather_df, x='temperature', y='bookings',
                             color='season', trendline='ols',
                             title="Temperature Impact on Bookings")
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        st.markdown("### 🌧️ Rain Probability vs Bookings")
        fig_rain = px.scatter(weather_df, x='rain_probability', y='bookings',
                             color='season', trendline='ols',
                             title="Rain Impact on Bookings")
        st.plotly_chart(fig_rain, use_container_width=True)
    
    # Seasonal analysis
    st.markdown("### 📅 Seasonal Weather Patterns")
    monthly_weather = weather_df.groupby(weather_df['date'].dt.month).agg({
        'temperature': 'mean',
        'rain_probability': 'mean', 
        'bookings': 'mean'
    }).round(2)
    
    monthly_weather.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig_seasonal = go.Figure()
    fig_seasonal.add_trace(go.Scatter(x=monthly_weather.index, y=monthly_weather['temperature'],
                                    mode='lines+markers', name='Avg Temperature'))
    fig_seasonal.add_trace(go.Scatter(x=monthly_weather.index, y=monthly_weather['bookings'],
                                    mode='lines+markers', name='Avg Bookings', yaxis='y2'))
    
    fig_seasonal.update_layout(
        title="Seasonal Weather and Booking Patterns",
        yaxis=dict(title="Temperature (°F)", side="left"),
        yaxis2=dict(title="Bookings", side="right", overlaying="y")
    )
    
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # Weather forecast integration
    st.markdown("### 🔮 7-Day Weather-Business Forecast")
    
    forecast_data = []
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        temp = 78 + np.random.normal(0, 5)
        rain = np.random.random() * 0.6
        predicted_bookings = max(0, 120 + (temp - 75) * 3 - rain * 50 + np.random.normal(0, 10))
        
        forecast_data.append({
            'Date': date.strftime('%m/%d'),
            'Day': date.strftime('%A'),
            'Temperature': f"{temp:.0f}°F",
            'Rain Chance': f"{rain:.0%}",
            'Predicted Bookings': int(predicted_bookings),
            'Recommended Action': 'Promote indoor activities' if rain > 0.4 else 'Promote outdoor activities'
        })
    
    forecast_df = pd.DataFrame(forecast_data)
    st.dataframe(forecast_df, use_container_width=True)

elif analysis_type == "Dynamic Pricing":
    st.markdown("## 💰 Dynamic Pricing Optimizer")
    
    # Generate pricing data
    pricing_df = create_pricing_data()
    
    # Pricing metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_current = pricing_df['current_price'].mean()
        st.metric("Average Current Price", f"${avg_current:.0f}")
    
    with col2:
        avg_optimal = pricing_df['optimal_price'].mean()
        st.metric("Average Optimal Price", f"${avg_optimal:.0f}")
    
    with col3:
        revenue_uplift = pricing_df['revenue_potential'].sum()
        st.metric("Monthly Revenue Potential", f"${revenue_uplift:,.0f}")
    
    with col4:
        avg_occupancy = pricing_df['occupancy'].mean()
        st.metric("Average Occupancy", f"{avg_occupancy:.1f}%")
    
    # Pricing optimization charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Price vs Occupancy")
        fig_price_occ = px.scatter(pricing_df, x='current_price', y='occupancy',
                                  color='revenue_potential', size='revenue_potential',
                                  title="Current Pricing Efficiency")
        st.plotly_chart(fig_price_occ, use_container_width=True)
    
    with col2:
        st.markdown("### 💎 Revenue Optimization Opportunities")
        fig_revenue = px.histogram(pricing_df, x='revenue_potential', nbins=20,
                                 title="Distribution of Revenue Potential")
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Pricing calendar
    st.markdown("### 📅 Dynamic Pricing Calendar")
    
    # Create a sample month view
    import calendar
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    month_data = pricing_df[pricing_df['date'].dt.month == current_month].copy()
    month_data['day'] = month_data['date'].dt.day
    
    # Pricing heatmap
    pricing_matrix = month_data.pivot_table(values='optimal_price', index='day', fill_value=0)
    
    if not pricing_matrix.empty:
        fig_calendar = px.imshow(pricing_matrix.T, 
                               title=f"Optimal Pricing Calendar - {calendar.month_name[current_month]}",
                               color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_calendar, use_container_width=True)
    
    # Pricing recommendations
    st.markdown("### 🎯 Today's Pricing Recommendations")
    
    today_data = pricing_df.iloc[0]  # Using first row as "today"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Current Strategy**")
        st.info(f"""
        💵 Current Price: ${today_data['current_price']:.0f}
        📊 Occupancy: {today_data['occupancy']:.1f}%
        📈 Revenue: ${today_data['current_price'] * today_data['occupancy']:.0f}
        """)
    
    with col2:
        st.markdown("**Recommended Strategy**")
        st.success(f"""
        💎 Optimal Price: ${today_data['optimal_price']:.0f}
        🎯 Target Occupancy: {today_data['occupancy'] + 5:.1f}%
        📈 Projected Revenue: ${today_data['optimal_price'] * (today_data['occupancy'] + 5):.0f}
        """)
    
    with col3:
        st.markdown("**Potential Impact**")
        revenue_increase = (today_data['optimal_price'] * (today_data['occupancy'] + 5)) - (today_data['current_price'] * today_data['occupancy'])
        st.warning(f"""
        💰 Revenue Increase: ${revenue_increase:.0f}
        📊 ROI: {(revenue_increase / (today_data['current_price'] * today_data['occupancy']) * 100):.1f}%
        ⏱️ Implementation: Immediate
        """)

elif analysis_type == "Customer Journey":
    st.markdown("## 🗺️ Customer Journey Mapping")
    
    # Journey stages
    stages = ['Awareness', 'Research', 'Consideration', 'Booking', 'Experience', 'Advocacy']
    
    # Journey metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg Journey Length", "12.3 days")
    with col2:
        st.metric("Top Entry Point", "Social Media (34%)")
    with col3:
        st.metric("Conversion Rate", "8.2%")
    with col4:
        st.metric("Avg Touchpoints", "5.7")
    
    # Journey funnel
    st.markdown("### 🔄 Customer Journey Funnel")
    journey_data = pd.DataFrame({
        'Stage': stages,
        'Visitors': [10000, 7500, 4200, 2100, 2000, 1200],
        'Conversion Rate': [100, 75, 42, 21, 20, 12],
        'Avg Time': ['0 days', '2.1 days', '5.3 days', '8.7 days', '14 days', '21 days']
    })
    
    fig_journey = px.funnel(journey_data, x='Visitors', y='Stage',
                           title="Customer Journey Conversion Funnel")
    st.plotly_chart(fig_journey, use_container_width=True)
    
    # Touchpoint analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📱 Digital Touchpoints")
        touchpoints = pd.DataFrame({
            'Touchpoint': ['Website', 'Social Media', 'Email', 'Mobile App', 'Online Ads', 'Reviews'],
            'Interactions': [8500, 6200, 4100, 3800, 2900, 2400],
            'Conversion Impact': [0.23, 0.18, 0.31, 0.19, 0.12, 0.35]
        })
        
        fig_touchpoints = px.scatter(touchpoints, x='Interactions', y='Conversion Impact',
                                   size='Interactions', color='Touchpoint',
                                   title="Touchpoint Performance")
        st.plotly_chart(fig_touchpoints, use_container_width=True)
    
    with col2:
        st.markdown("### 🕒 Journey Timeline")
        timeline_data = pd.DataFrame({
            'Day': range(1, 15),
            'Website Visits': np.random.poisson(50, 14),
            'Social Interactions': np.random.poisson(30, 14),
            'Email Opens': np.random.poisson(20, 14)
        })
        
        fig_timeline = px.line(timeline_data, x='Day', 
                              y=['Website Visits', 'Social Interactions', 'Email Opens'],
                              title="Customer Interaction Timeline")
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Journey segments
    st.markdown("### 👥 Customer Segments Journey")
    
    segments = ['Luxury Seekers', 'Family Travelers', 'Adventure Enthusiasts', 'Budget Conscious', 'Business Travelers']
    segment_data = []
    
    for segment in segments:
        for stage in stages:
            value = np.random.randint(50, 300)
            segment_data.append({'Segment': segment, 'Stage': stage, 'Count': value})
    
    segment_df = pd.DataFrame(segment_data)
    
    fig_segments = px.sunburst(segment_df, path=['Segment', 'Stage'], values='Count',
                              title="Journey Stages by Customer Segment")
    st.plotly_chart(fig_segments, use_container_width=True)

elif analysis_type == "Marketing Attribution":
    st.markdown("## 🎯 Marketing Attribution Analysis")
    
    # Attribution metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Marketing Spend", "$124,500")
    with col2:
        st.metric("Revenue Attributed", "$892,300")
    with col3:
        st.metric("ROAS", "7.2x")
    with col4:
        st.metric("CAC", "$87")
    
    # Channel performance
    st.markdown("### 📊 Marketing Channel Performance")
    
    channels = ['Google Ads', 'Facebook', 'Instagram', 'Email', 'Organic Search', 'Direct', 'Referral']
    channel_data = pd.DataFrame({
        'Channel': channels,
        'Spend': [35000, 28000, 22000, 15000, 12000, 8000, 4500],
        'Revenue': [245000, 189000, 156000, 98000, 125000, 67000, 32300],
        'Conversions': [580, 420, 390, 280, 350, 180, 95],
        'ROAS': [7.0, 6.8, 7.1, 6.5, 10.4, 8.4, 7.2]
    })
    
    # ROAS by channel
    col1, col2 = st.columns(2)
    
    with col1:
        fig_roas = px.bar(channel_data, x='Channel', y='ROAS',
                         title="Return on Ad Spend by Channel")
        st.plotly_chart(fig_roas, use_container_width=True)
    
    with col2:
        fig_spend = px.pie(channel_data, values='Spend', names='Channel',
                          title="Marketing Spend Distribution")
        st.plotly_chart(fig_spend, use_container_width=True)
    
    # Attribution models comparison
    st.markdown("### 🎲 Attribution Model Comparison")
    
    attribution_models = pd.DataFrame({
        'Channel': channels,
        'First Touch': [25, 18, 15, 12, 20, 8, 2],
        'Last Touch': [22, 20, 18, 10, 15, 12, 3],
        'Linear': [20, 19, 16, 11, 17, 10, 7],
        'Time Decay': [18, 21, 17, 12, 16, 11, 5],
        'Data Driven': [23, 19, 16, 9, 18, 10, 5]
    })
    
    fig_attribution = px.bar(attribution_models, x='Channel',
                            y=['First Touch', 'Last Touch', 'Linear', 'Time Decay', 'Data Driven'],
                            title="Revenue Attribution by Model (%)")
    st.plotly_chart(fig_attribution, use_container_width=True)
    
    # Customer lifetime value by channel
    st.markdown("### 💎 Customer Lifetime Value by Acquisition Channel")
    
    clv_data = pd.DataFrame({
        'Channel': channels,
        'CLV': [1250, 890, 920, 1450, 1680, 1120, 980],
        'Avg Order Value': [420, 380, 390, 510, 580, 450, 390],
        'Repeat Purchase Rate': [0.45, 0.38, 0.41, 0.52, 0.61, 0.48, 0.42]
    })
    
    fig_clv = px.scatter(clv_data, x='Avg Order Value', y='CLV',
                        size='Repeat Purchase Rate', color='Channel',
                        title="CLV vs AOV by Channel")
    st.plotly_chart(fig_clv, use_container_width=True)

elif analysis_type == "Event Impact":
    st.markdown("## 🎊 Event Impact Analysis")
    
    # Event calendar with impact
    st.markdown("### 📅 Hawaii Events Calendar & Tourism Impact")
    
    events_data = pd.DataFrame({
        'Event': ['Honolulu Marathon', 'Lei Day', 'Merrie Monarch Festival', 'King Kamehameha Day', 
                 'Aloha Festivals', 'Hawaii Food & Wine Festival', 'Triple Crown of Surfing', 'New Year'],
        'Date': ['Dec 8', 'May 1', 'Apr 14-20', 'Jun 11', 'Sep 1-30', 'Oct 15-Nov 5', 'Nov 12-Dec 20', 'Dec 31'],
        'Expected Visitors': [15000, 8000, 25000, 12000, 45000, 18000, 35000, 50000],
        'Revenue Impact': ['+35%', '+20%', '+60%', '+25%', '+80%', '+40%', '+70%', '+120%'],
        'Booking Surge Start': ['-14 days', '-7 days', '-21 days', '-10 days', '-30 days', '-20 days', '-25 days', '-45 days']
    })
    
    st.dataframe(events_data, use_container_width=True)
    
    # Event impact visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Event Impact on Bookings")
        # Simulate booking pattern around events
        dates = pd.date_range('2024-01-01', periods=365)
        bookings = []
        
        for date in dates:
            base_bookings = 100
            # Add spikes for major events
            if date.month == 12 and date.day in [8, 31]:  # Marathon, New Year
                base_bookings *= 2.2
            elif date.month == 11:  # Triple Crown season
                base_bookings *= 1.7
            elif date.month == 9:  # Aloha Festivals
                base_bookings *= 1.8
            elif date.month == 4 and 14 <= date.day <= 20:  # Merrie Monarch
                base_bookings *= 1.6
                
            bookings.append(int(base_bookings + np.random.normal(0, 10)))
        
        event_impact_df = pd.DataFrame({'Date': dates, 'Bookings': bookings})
        
        fig_events = px.line(event_impact_df, x='Date', y='Bookings',
                           title="Annual Booking Pattern with Event Impact")
        st.plotly_chart(fig_events, use_container_width=True)
    
    with col2:
        st.markdown("### 🌊 Event Category Performance")
        event_categories = pd.DataFrame({
            'Category': ['Cultural', 'Sports', 'Music', 'Food', 'Holiday', 'Business'],
            'Avg Impact': [65, 45, 40, 35, 95, 25],
            'Duration': [7, 3, 2, 5, 14, 4]
        })
        
        fig_categories = px.scatter(event_categories, x='Duration', y='Avg Impact',
                                  size='Avg Impact', color='Category',
                                  title="Event Impact vs Duration by Category")
        st.plotly_chart(fig_categories, use_container_width=True)
    
    # Event recommendation engine
    st.markdown("### 🎯 Event-Based Marketing Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔥 Upcoming High-Impact Events**")
        st.success("""
        **Honolulu Marathon** (Dec 8)
        • Expected +35% bookings
        • Start marketing: Nov 24
        • Focus: Sports tourists, mainland US
        """)
        
    with col2:
        st.markdown("**📈 Pricing Opportunities**")
        st.info("""
        **Triple Crown Season** (Nov-Dec)
        • Increase rates 40-70%
        • Minimum 3-night stays
        • Package with surf experiences
        """)
    
    with col3:
        st.markdown("**🎪 Partnership Opportunities**")
        st.warning("""
        **Aloha Festivals** (Sep)
        • Partner with event organizers
        • Create cultural packages
        • 80% revenue increase potential
        """)

elif analysis_type == "Activity Recommendations":
    st.markdown("## 🏖️ Activity Recommendation Engine")
    
    # Current conditions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Weather", "82°F Sunny")
    with col2:
        st.metric("UV Index", "8 (High)")
    with col3:
        st.metric("Wind Speed", "12 mph")
    with col4:
        st.metric("Wave Height", "3-5 ft")
    
    # Activity recommendations
    st.markdown("### 🌟 Today's Top Activity Recommendations")
    
    activities = [
        {"name": "Snorkeling at Hanauma Bay", "score": 95, "reason": "Perfect visibility, calm waters", "icon": "🤿"},
        {"name": "Hiking Diamond Head", "score": 88, "reason": "Clear skies, cool morning", "icon": "🥾"},
        {"name": "Surfing North Shore", "score": 82, "reason": "Good waves, favorable wind", "icon": "🏄‍♂️"},
        {"name": "Pearl Harbor Tour", "score": 85, "reason": "Indoor/outdoor mix", "icon": "🚢"},
        {"name": "Luau Experience", "score": 90, "reason": "Perfect evening weather", "icon": "🌺"}
    ]
    
    for i, activity in enumerate(activities):
        col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
        
        with col1:
            st.markdown(f"## {activity['icon']}")
        
        with col2:
            st.markdown(f"**{activity['name']}**")
            st.caption(activity['reason'])
        
        with col3:
            st.metric("Match Score", f"{activity['score']}%")
        
        with col4:
            if st.button(f"Book Now", key=f"book_{i}"):
                st.success(f"Redirecting to {activity['name']} booking...")
    
    # Activity heatmap by time and weather
    st.markdown("### 🕐 Activity Recommendation Heatmap")
    
    # Create sample heatmap data
    hours = [f"{h}:00" for h in range(6, 20)]
    weather_conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Windy']
    
    # Generate recommendation scores
    heatmap_data = []
    activities_short = ['Beach', 'Hiking', 'Tours', 'Water Sports', 'Cultural']
    
    for condition in weather_conditions:
        row = []
        for hour in range(len(hours)):
            # Different activities peak at different times/conditions
            if condition == 'Sunny':
                if 6 <= hour <= 10:  # Morning
                    row.append(np.random.randint(80, 100))
                else:
                    row.append(np.random.randint(60, 90))
            elif condition == 'Light Rain':
                row.append(np.random.randint(30, 70))
            else:
                row.append(np.random.randint(50, 85))
        heatmap_data.append(row)
    
    fig_heatmap = px.imshow(heatmap_data, 
                           x=hours, y=weather_conditions,
                           color_continuous_scale='RdYlGn',
                           title="Activity Recommendation Scores by Time & Weather")
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Personalized recommendations
    st.markdown("### 🎯 Personalized Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Set Your Preferences**")
        activity_type = st.selectbox("Activity Type", 
                                   ['Adventure', 'Relaxation', 'Cultural', 'Family-Friendly', 'Romantic'])
        fitness_level = st.slider("Fitness Level", 1, 5, 3)
        budget_range = st.select_slider("Budget Range", 
                                      ['$', '$$', '$$$', '$$$$'], value='$$')
        group_size = st.number_input("Group Size", 1, 20, 2)
    
    with col2:
        st.markdown("**Your Customized Recommendations**")
        
        recommendations = {
            'Adventure': ['Zipline Tours', 'Volcano Helicopter Tour', 'ATV Rides'],
            'Relaxation': ['Spa Day', 'Beach Lounging', 'Sunset Cruise'],
            'Cultural': ['Polynesian Cultural Center', 'Historic Honolulu', 'Lei Making'],
            'Family-Friendly': ['Aquarium Visit', 'Mini Golf', 'Beach Games'],
            'Romantic': ['Sunset Dinner Cruise', 'Couples Massage', 'Private Beach']
        }
        
        for rec in recommendations.get(activity_type, []):
            st.success(f"✨ {rec}")
            st.caption(f"Perfect for {group_size} people • {budget_range} budget range")

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

# Add refresh functionality
if st.button("🔄 Auto-refresh (Live Mode)", key="auto_refresh"):
    st.rerun()