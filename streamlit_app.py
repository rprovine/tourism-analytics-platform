import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Tourism Analytics Platform - LeniLani Consulting",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=LeniLani+Consulting", use_container_width=True)
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
        ["Overview", "Sentiment Analysis", "Revenue Analytics", "Demand Forecasting", "Competitive Analysis"]
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