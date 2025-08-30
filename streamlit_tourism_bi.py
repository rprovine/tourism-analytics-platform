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

# Page configuration
st.set_page_config(
    page_title="Hawaii Tourism Intelligence Platform",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .sub-header {
        font-size: 1.5rem;
        color: #4a5568;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .data-source-badge {
        background: #48bb78;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Generate mock tourism business data
@st.cache_data
def generate_tourism_prospects():
    """Generate mock tourism business prospects with AI scoring"""
    businesses = [
        # Hotels & Resorts
        {"name": "Royal Hawaiian Hotel", "type": "Luxury Resort", "island": "Oahu", "category": "Accommodation", 
         "rooms": 528, "rating": 4.6, "annual_revenue": "$85M", "employees": 450},
        {"name": "Grand Wailea Resort", "type": "Resort", "island": "Maui", "category": "Accommodation",
         "rooms": 776, "rating": 4.5, "annual_revenue": "$120M", "employees": 600},
        {"name": "Four Seasons Hualalai", "type": "Luxury Resort", "island": "Big Island", "category": "Accommodation",
         "rooms": 243, "rating": 4.8, "annual_revenue": "$95M", "employees": 380},
        
        # Tour Operators
        {"name": "Blue Hawaiian Helicopters", "type": "Tour Operator", "island": "Multi-Island", "category": "Activities",
         "tours_daily": 25, "rating": 4.7, "annual_revenue": "$45M", "employees": 120},
        {"name": "Roberts Hawaii", "type": "Transportation", "island": "Multi-Island", "category": "Transportation",
         "fleet_size": 300, "rating": 4.2, "annual_revenue": "$180M", "employees": 1200},
        {"name": "Atlantis Submarines", "type": "Tour Operator", "island": "Oahu", "category": "Activities",
         "tours_daily": 8, "rating": 4.4, "annual_revenue": "$22M", "employees": 85},
        
        # Restaurants
        {"name": "Mama's Fish House", "type": "Restaurant", "island": "Maui", "category": "Dining",
         "seats": 180, "rating": 4.7, "annual_revenue": "$18M", "employees": 95},
        {"name": "Duke's Waikiki", "type": "Restaurant", "island": "Oahu", "category": "Dining",
         "seats": 250, "rating": 4.5, "annual_revenue": "$24M", "employees": 120},
        
        # Activity Providers
        {"name": "Maui Ocean Center", "type": "Attraction", "island": "Maui", "category": "Activities",
         "visitors_annual": 450000, "rating": 4.4, "annual_revenue": "$15M", "employees": 65},
        {"name": "Polynesian Cultural Center", "type": "Cultural Attraction", "island": "Oahu", "category": "Activities",
         "visitors_annual": 800000, "rating": 4.3, "annual_revenue": "$40M", "employees": 350},
        
        # Travel Agencies
        {"name": "Hawaii Travel Bureau", "type": "Travel Agency", "island": "Oahu", "category": "Travel Services",
         "bookings_annual": 25000, "rating": 4.5, "annual_revenue": "$35M", "employees": 85},
        {"name": "Aloha Travel Planners", "type": "Travel Agency", "island": "Multi-Island", "category": "Travel Services",
         "bookings_annual": 18000, "rating": 4.4, "annual_revenue": "$28M", "employees": 65},
    ]
    
    # Add AI scoring and analysis
    for business in businesses:
        # Technology Readiness Score (0-100)
        tech_factors = random.randint(60, 95)
        business['tech_readiness'] = tech_factors
        
        # Growth Potential Score (0-100)
        growth_factors = random.randint(70, 98)
        business['growth_potential'] = growth_factors
        
        # AI Priority Score (combination of factors)
        business['ai_priority_score'] = round((tech_factors + growth_factors) / 2 + random.randint(-5, 5), 1)
        
        # Pain Points (AI-identified)
        pain_points = [
            "Manual booking management",
            "Seasonal demand fluctuations",
            "Customer experience tracking",
            "Revenue optimization",
            "Staff scheduling complexity",
            "Inventory management",
            "Marketing ROI tracking",
            "Guest satisfaction monitoring"
        ]
        business['pain_points'] = random.sample(pain_points, 3)
        
        # Recommended Solutions
        solutions = [
            "AI-Powered Booking System",
            "Dynamic Pricing Engine",
            "Predictive Analytics Dashboard",
            "Customer Sentiment Analysis",
            "Automated Marketing Platform",
            "Revenue Management System",
            "Staff Optimization Tool",
            "Guest Experience Platform"
        ]
        business['recommended_solutions'] = random.sample(solutions, 3)
        
        # Data Collection Status
        business['last_scraped'] = datetime.now() - timedelta(days=random.randint(0, 7))
        business['data_sources'] = random.sample([
            "Google Business", "TripAdvisor", "Yelp", "Booking.com", 
            "Expedia", "Hotels.com", "OpenTable", "Instagram"
        ], random.randint(3, 5))
    
    return pd.DataFrame(businesses)

@st.cache_data
def generate_market_intelligence():
    """Generate market intelligence data"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = []
    
    for date in dates:
        # Tourism arrival trends
        base_arrivals = 30000
        seasonal_factor = 1.3 if date.month in [12, 1, 2, 6, 7, 8] else 0.9
        trend = base_arrivals * seasonal_factor * (1 + 0.1 * np.sin(date.dayofyear / 365 * 2 * np.pi))
        
        data.append({
            'date': date,
            'visitor_arrivals': int(trend + np.random.normal(0, 1000)),
            'hotel_occupancy': min(95, max(60, 75 + 15 * seasonal_factor + np.random.normal(0, 5))),
            'avg_daily_spend': 250 + 50 * seasonal_factor + np.random.normal(0, 20),
            'flight_searches': int(50000 * seasonal_factor + np.random.normal(0, 5000)),
            'competitor_rate': 350 + 100 * seasonal_factor + np.random.normal(0, 30)
        })
    
    return pd.DataFrame(data)

@st.cache_data
def generate_competitor_analysis():
    """Generate competitor analysis data"""
    competitors = []
    
    for i in range(10):
        competitors.append({
            'competitor': f"Competitor {chr(65+i)}",
            'market_share': random.uniform(5, 20),
            'avg_rating': round(random.uniform(4.0, 4.8), 1),
            'price_index': round(random.uniform(0.8, 1.3), 2),
            'online_mentions': random.randint(1000, 10000),
            'sentiment_score': round(random.uniform(0.6, 0.9), 2),
            'growth_rate': round(random.uniform(-5, 25), 1)
        })
    
    return pd.DataFrame(competitors)

# Sidebar navigation
def sidebar_navigation():
    with st.sidebar:
        st.markdown("# 🌺 Hawaii Tourism BI")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Landing Page", "📊 Dashboard", "🎯 Prospect Discovery", 
             "🤖 AI Analysis", "📈 Market Intelligence", "🔄 Data Collection",
             "⚙️ Settings"]
        )
        
        st.markdown("---")
        st.markdown("### Data Sources")
        st.markdown("""
        <div style='font-size: 0.9rem;'>
        <span class='data-source-badge'>✅ Google Business</span>
        <span class='data-source-badge'>✅ TripAdvisor</span>
        <span class='data-source-badge'>✅ Booking.com</span>
        <span class='data-source-badge'>✅ Yelp</span>
        <span class='data-source-badge'>✅ Instagram</span>
        <span class='data-source-badge'>✅ Custom Websites</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### System Status")
        st.success("🟢 All Systems Operational")
        st.info(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
    return page

def landing_page():
    """Display the landing page"""
    st.markdown("<h1 class='main-header'>Hawaii Tourism Intelligence Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>AI-Powered Business Intelligence for Hawaii's Tourism Industry</p>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h2>12,500+</h2>
            <p>Tourism Businesses Tracked</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h2>8</h2>
            <p>Data Sources Integrated</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h2>24/7</h2>
            <p>Real-Time Monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <h2>96%</h2>
            <p>AI Accuracy Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How it works
    st.markdown("## 🚀 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Data Collection
        Automatically scrape and aggregate data from:
        - **Google Maps & Business Profiles**
        - **TripAdvisor Reviews & Ratings**
        - **Booking.com & Expedia Listings**
        - **Yelp Business Information**
        - **Social Media (Instagram, Facebook)**
        - **Flight Search Trends**
        - **Weather & Event Data**
        - **Custom Websites You Specify**
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ AI Analysis
        Our AI engine analyzes each business for:
        - **Technology Readiness Score**
        - **Growth Potential Assessment**
        - **Market Position Analysis**
        - **Pain Point Identification**
        - **Revenue Optimization Opportunities**
        - **Competitive Positioning**
        - **Sentiment Analysis**
        - **Demand Forecasting**
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Lead Generation
        Get prioritized prospects with:
        - **AI Priority Scoring (0-100)**
        - **Custom Filtering Parameters**
        - **Industry Segmentation**
        - **Geographic Targeting**
        - **Size & Revenue Filters**
        - **Automated Alerts**
        - **CRM Integration**
        - **Engagement Recommendations**
        """)
    
    st.markdown("---")
    
    # Features
    st.markdown("## ✨ Key Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        ### 📊 Comprehensive Analytics
        - Real-time visitor arrival trends
        - Hotel occupancy predictions
        - Seasonal demand patterns
        - Price optimization insights
        - Competitor benchmarking
        - Market share analysis
        """)
        
        st.markdown("""
        ### 🎯 Smart Lead Discovery
        - AI-powered prospect scoring
        - Technology readiness assessment
        - Growth potential analysis
        - Pain point identification
        - Solution recommendations
        - Contact information enrichment
        """)
    
    with feature_col2:
        st.markdown("""
        ### 🤖 AI-Powered Intelligence
        - Natural language processing of reviews
        - Sentiment analysis across platforms
        - Predictive demand forecasting
        - Dynamic pricing recommendations
        - Automated competitive analysis
        - Custom alert configurations
        """)
        
        st.markdown("""
        ### 🔄 Automated Workflows
        - Scheduled data collection
        - Real-time monitoring
        - Automatic report generation
        - Email notifications
        - API integrations
        - Custom data pipelines
        """)
    
    st.markdown("---")
    
    # Customization
    st.markdown("## ⚙️ Fully Customizable")
    st.info("""
    **Tailor the platform to your specific needs:**
    - 🎯 **Target Criteria**: Define your ideal customer profile (hotels, tours, restaurants, etc.)
    - 🗺️ **Geographic Focus**: Select specific islands, regions, or areas
    - 💰 **Revenue Filters**: Target businesses within your service capacity
    - 📊 **Scoring Weights**: Customize how prospects are evaluated and ranked
    - 📅 **Collection Schedule**: Set how often data is updated
    - 🔔 **Alert Thresholds**: Configure when to receive notifications
    """)
    
    st.markdown("---")
    
    # Benefits
    st.markdown("## 💪 Benefits for Your Business")
    
    benefits = [
        "🎯 **10x More Qualified Leads** - AI identifies your perfect prospects automatically",
        "⏰ **Save 30+ Hours Weekly** - Eliminate manual research and data entry",
        "📈 **35% Higher Conversion** - Better intelligence means better targeting",
        "🏆 **Competitive Advantage** - Stay ahead with real-time market insights",
        "💰 **Revenue Growth** - Optimize pricing and identify new opportunities",
        "🤝 **Better Partnerships** - Find complementary businesses to collaborate with"
    ]
    
    for benefit in benefits:
        st.markdown(f"- {benefit}")
    
    st.markdown("---")
    
    # Call to action
    st.markdown("## 🌟 Ready to Transform Your Tourism Business?")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Free 14-Day Trial", use_container_width=True):
            st.success("Welcome! Navigate to the Dashboard to begin exploring.")
        if st.button("📊 View Live Demo Dashboard", use_container_width=True):
            st.info("Select 'Dashboard' from the sidebar to see live data.")

def dashboard_page():
    """Display the main dashboard"""
    st.title("📊 Tourism Intelligence Dashboard")
    
    # Load data
    prospects_df = generate_tourism_prospects()
    market_df = generate_market_intelligence()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prospects", len(prospects_df), "↑ 12%")
    with col2:
        high_priority = len(prospects_df[prospects_df['ai_priority_score'] > 85])
        st.metric("High Priority", high_priority, "↑ 3")
    with col3:
        avg_score = prospects_df['ai_priority_score'].mean()
        st.metric("Avg AI Score", f"{avg_score:.1f}", "↑ 2.3")
    with col4:
        total_revenue = sum([float(rev.replace('$', '').replace('M', '')) for rev in prospects_df['annual_revenue']])
        st.metric("Total Market Value", f"${total_revenue:.0f}M", "↑ 8%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Prospects by Category
        fig_category = px.pie(
            prospects_df, 
            names='category', 
            title='Prospects by Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # AI Scores Distribution
        fig_scores = px.histogram(
            prospects_df,
            x='ai_priority_score',
            nbins=20,
            title='AI Priority Score Distribution',
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    # Market Trends
    st.markdown("### 📈 Market Trends")
    
    # Create tabs for different metrics
    tab1, tab2, tab3 = st.tabs(["Visitor Arrivals", "Hotel Occupancy", "Average Daily Spend"])
    
    with tab1:
        fig_arrivals = px.line(
            market_df,
            x='date',
            y='visitor_arrivals',
            title='Daily Visitor Arrivals Trend'
        )
        st.plotly_chart(fig_arrivals, use_container_width=True)
    
    with tab2:
        fig_occupancy = px.line(
            market_df,
            x='date',
            y='hotel_occupancy',
            title='Hotel Occupancy Rate (%)'
        )
        st.plotly_chart(fig_occupancy, use_container_width=True)
    
    with tab3:
        fig_spend = px.line(
            market_df,
            x='date',
            y='avg_daily_spend',
            title='Average Daily Tourist Spend ($)'
        )
        st.plotly_chart(fig_spend, use_container_width=True)

def prospect_discovery_page():
    """Display prospect discovery and lead generation page"""
    st.title("🎯 Prospect Discovery & Lead Generation")
    
    # Filters
    st.markdown("### 🔍 Filter Prospects")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.multiselect(
            "Category",
            ["Accommodation", "Activities", "Dining", "Transportation", "Travel Services"],
            default=["Accommodation", "Activities"]
        )
    
    with col2:
        island_filter = st.multiselect(
            "Island",
            ["Oahu", "Maui", "Big Island", "Kauai", "Multi-Island"],
            default=["Oahu", "Maui"]
        )
    
    with col3:
        min_score = st.slider("Min AI Score", 0, 100, 70)
    
    with col4:
        sort_by = st.selectbox(
            "Sort By",
            ["AI Score", "Revenue", "Growth Potential", "Tech Readiness"]
        )
    
    # Load and filter data
    prospects_df = generate_tourism_prospects()
    
    # Apply filters
    if category_filter:
        prospects_df = prospects_df[prospects_df['category'].isin(category_filter)]
    if island_filter:
        prospects_df = prospects_df[prospects_df['island'].isin(island_filter)]
    prospects_df = prospects_df[prospects_df['ai_priority_score'] >= min_score]
    
    # Sort
    sort_mapping = {
        "AI Score": "ai_priority_score",
        "Revenue": "annual_revenue",
        "Growth Potential": "growth_potential",
        "Tech Readiness": "tech_readiness"
    }
    prospects_df = prospects_df.sort_values(sort_mapping[sort_by], ascending=False)
    
    st.markdown(f"### 📋 Found {len(prospects_df)} Prospects")
    
    # Display prospects
    for idx, prospect in prospects_df.iterrows():
        with st.expander(f"🏢 **{prospect['name']}** - Score: {prospect['ai_priority_score']:.1f}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Business Info**")
                st.write(f"Type: {prospect['type']}")
                st.write(f"Category: {prospect['category']}")
                st.write(f"Island: {prospect['island']}")
                st.write(f"Rating: ⭐ {prospect['rating']}")
                st.write(f"Revenue: {prospect['annual_revenue']}")
                st.write(f"Employees: {prospect['employees']}")
            
            with col2:
                st.markdown("**AI Analysis**")
                st.write(f"Tech Readiness: {prospect['tech_readiness']}%")
                st.write(f"Growth Potential: {prospect['growth_potential']}%")
                st.write(f"Priority Score: {prospect['ai_priority_score']}")
                
                st.markdown("**Pain Points:**")
                for pain in prospect['pain_points']:
                    st.write(f"• {pain}")
            
            with col3:
                st.markdown("**Recommended Solutions**")
                for solution in prospect['recommended_solutions']:
                    st.write(f"✅ {solution}")
                
                st.markdown("**Data Sources:**")
                for source in prospect['data_sources']:
                    st.write(f"• {source}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📧 Contact", key=f"contact_{idx}"):
                    st.success("Contact information exported to CRM")
            with col2:
                if st.button(f"📊 Full Analysis", key=f"analysis_{idx}"):
                    st.info("Generating detailed analysis report...")
            with col3:
                if st.button(f"📅 Schedule Demo", key=f"demo_{idx}"):
                    st.success("Demo scheduling link sent")

def ai_analysis_page():
    """Display AI analysis and insights"""
    st.title("🤖 AI-Powered Analysis & Insights")
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Sentiment Analysis", "Demand Forecasting", "Competitive Intelligence", "Price Optimization"]
    )
    
    if analysis_type == "Sentiment Analysis":
        st.markdown("### 😊 Customer Sentiment Analysis")
        
        # Generate sentiment data
        dates = pd.date_range(start='2024-01-01', periods=30)
        sentiment_data = pd.DataFrame({
            'date': dates,
            'positive': np.random.uniform(0.6, 0.8, 30),
            'neutral': np.random.uniform(0.15, 0.25, 30),
            'negative': np.random.uniform(0.05, 0.15, 30)
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sentiment_data['date'], y=sentiment_data['positive'], 
                                 name='Positive', fill='tonexty', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=sentiment_data['date'], y=sentiment_data['neutral'], 
                                 name='Neutral', fill='tonexty', line=dict(color='gray')))
        fig.add_trace(go.Scatter(x=sentiment_data['date'], y=sentiment_data['negative'], 
                                 name='Negative', fill='tonexty', line=dict(color='red')))
        
        fig.update_layout(title='Sentiment Trend Analysis', yaxis_title='Sentiment Score')
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        st.markdown("### 💡 AI-Generated Insights")
        insights = [
            "✅ Overall sentiment has improved by 12% over the past month",
            "⚠️ Negative sentiment spikes correlate with weather events",
            "📈 Positive mentions increased 25% after new amenity launch",
            "🎯 Key positive themes: 'beautiful location', 'excellent service', 'great value'",
            "🔧 Areas for improvement: 'parking', 'wait times', 'breakfast options'"
        ]
        for insight in insights:
            st.write(insight)
    
    elif analysis_type == "Demand Forecasting":
        st.markdown("### 📈 AI Demand Forecasting")
        
        # Generate forecast data
        dates_future = pd.date_range(start='2024-01-01', periods=365)
        historical = np.sin(np.linspace(0, 4*np.pi, 200)) * 50 + 200 + np.random.normal(0, 10, 200)
        forecast = np.sin(np.linspace(4*np.pi, 6*np.pi, 165)) * 50 + 210 + np.random.normal(0, 5, 165)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates_future[:200], y=historical, name='Historical', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=dates_future[200:], y=forecast, name='AI Forecast', 
                                 line=dict(color='red', dash='dash')))
        
        fig.update_layout(title='365-Day Demand Forecast', yaxis_title='Expected Bookings/Day')
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peak Season Start", "Dec 15, 2024", "23 days earlier")
        with col2:
            st.metric("Expected Peak Demand", "342 bookings/day", "↑ 18%")
        with col3:
            st.metric("Confidence Level", "94%", "High accuracy")
    
    elif analysis_type == "Competitive Intelligence":
        st.markdown("### 🏆 Competitive Intelligence Dashboard")
        
        competitors_df = generate_competitor_analysis()
        
        # Market share visualization
        fig_market = px.pie(
            competitors_df,
            values='market_share',
            names='competitor',
            title='Market Share Distribution'
        )
        st.plotly_chart(fig_market, use_container_width=True)
        
        # Competitive matrix
        fig_matrix = px.scatter(
            competitors_df,
            x='price_index',
            y='avg_rating',
            size='market_share',
            color='growth_rate',
            hover_data=['competitor'],
            title='Competitive Positioning Matrix',
            labels={'price_index': 'Price Index', 'avg_rating': 'Average Rating'}
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    elif analysis_type == "Price Optimization":
        st.markdown("### 💰 AI-Powered Price Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Pricing**")
            st.metric("Average Daily Rate", "$425", "↑ $12")
            st.metric("Occupancy Rate", "78%", "↑ 3%")
            st.metric("RevPAR", "$331", "↑ $15")
        
        with col2:
            st.markdown("**AI Recommended**")
            st.metric("Optimal Daily Rate", "$465", "+$40")
            st.metric("Projected Occupancy", "75%", "-3%")
            st.metric("Projected RevPAR", "$349", "+$18")
        
        st.info("💡 **AI Recommendation**: Increase rates by 9.4% during peak season. Expected revenue increase of $2.3M annually.")

def data_collection_page():
    """Display data collection and monitoring page"""
    st.title("🔄 Data Collection & Monitoring")
    
    st.markdown("### 📊 Data Collection Status")
    
    # Data source status
    sources = [
        {"name": "Google Business", "status": "Active", "last_run": "2 hours ago", "records": 3245, "health": 98},
        {"name": "TripAdvisor", "status": "Active", "last_run": "4 hours ago", "records": 2890, "health": 95},
        {"name": "Booking.com", "status": "Active", "last_run": "1 hour ago", "records": 1567, "health": 99},
        {"name": "Yelp", "status": "Active", "last_run": "3 hours ago", "records": 2134, "health": 97},
        {"name": "Instagram", "status": "Scheduled", "last_run": "6 hours ago", "records": 4567, "health": 92},
        {"name": "Custom Website", "status": "Active", "last_run": "30 min ago", "records": 892, "health": 100},
    ]
    
    for source in sources:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        
        with col1:
            if source['status'] == 'Active':
                st.success(f"🟢 {source['name']}")
            else:
                st.warning(f"🟡 {source['name']}")
        
        with col2:
            st.write(f"Status: {source['status']}")
        
        with col3:
            st.write(f"Last: {source['last_run']}")
        
        with col4:
            st.write(f"Records: {source['records']:,}")
        
        with col5:
            st.progress(source['health'] / 100)
    
    st.markdown("---")
    
    # Collection triggers
    st.markdown("### 🚀 Manual Collection Triggers")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Run All Sources", use_container_width=True):
            st.success("All data sources triggered for collection")
    
    with col2:
        if st.button("🌐 Custom Scrape", use_container_width=True):
            st.info("Enter URL in settings to scrape custom website")
    
    with col3:
        if st.button("📱 Social Media", use_container_width=True):
            st.success("Social media collection initiated")
    
    with col4:
        if st.button("✈️ Flight Data", use_container_width=True):
            st.success("Flight search data collection started")
    
    st.markdown("---")
    
    # Collection logs
    st.markdown("### 📝 Recent Collection Logs")
    
    logs = [
        {"time": "10:30 AM", "source": "Google Business", "action": "Scraped", "status": "Success", "details": "245 new records"},
        {"time": "10:15 AM", "source": "TripAdvisor", "action": "Updated", "status": "Success", "details": "890 reviews analyzed"},
        {"time": "09:45 AM", "source": "Custom Website", "action": "Scraped", "status": "Success", "details": "15 new businesses found"},
        {"time": "09:30 AM", "source": "Yelp", "action": "Scraped", "status": "Warning", "details": "Rate limited, retrying..."},
        {"time": "09:00 AM", "source": "All Sources", "action": "Scheduled", "status": "Success", "details": "Daily collection completed"},
    ]
    
    for log in logs:
        if log['status'] == 'Success':
            st.success(f"**{log['time']}** - {log['source']}: {log['details']}")
        elif log['status'] == 'Warning':
            st.warning(f"**{log['time']}** - {log['source']}: {log['details']}")
        else:
            st.error(f"**{log['time']}** - {log['source']}: {log['details']}")

def settings_page():
    """Display settings and configuration page"""
    st.title("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Data Sources", "Scoring Criteria", "Alerts", "Integration"])
    
    with tab1:
        st.markdown("### 🌐 Configure Data Sources")
        
        st.markdown("**Add Custom Website**")
        custom_url = st.text_input("Website URL to Scrape")
        scrape_frequency = st.selectbox("Scrape Frequency", ["Hourly", "Daily", "Weekly", "Monthly"])
        if st.button("Add Website"):
            st.success(f"Added {custom_url} to scraping queue")
        
        st.markdown("**API Integrations**")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("TripAdvisor API Key", type="password")
            st.text_input("Google Places API Key", type="password")
        with col2:
            st.text_input("Booking.com Partner ID", type="password")
            st.text_input("Instagram Access Token", type="password")
    
    with tab2:
        st.markdown("### 🎯 Customize Scoring Criteria")
        
        st.markdown("**Weight Factors (Total must = 100%)**")
        tech_weight = st.slider("Technology Readiness Weight", 0, 100, 25)
        growth_weight = st.slider("Growth Potential Weight", 0, 100, 25)
        revenue_weight = st.slider("Revenue Size Weight", 0, 100, 25)
        engagement_weight = st.slider("Engagement Level Weight", 0, 100, 25)
        
        total = tech_weight + growth_weight + revenue_weight + engagement_weight
        if total != 100:
            st.error(f"Total weight is {total}%. Please adjust to equal 100%.")
        else:
            st.success("✅ Scoring weights configured correctly")
    
    with tab3:
        st.markdown("### 🔔 Alert Configuration")
        
        st.markdown("**New Prospect Alerts**")
        min_score_alert = st.slider("Minimum Score for Alert", 0, 100, 85)
        alert_email = st.text_input("Alert Email Address")
        
        st.markdown("**Alert Triggers**")
        st.checkbox("New high-priority prospect found", value=True)
        st.checkbox("Competitor makes significant change", value=True)
        st.checkbox("Market trend shift detected", value=False)
        st.checkbox("Data collection issue", value=True)
    
    with tab4:
        st.markdown("### 🔗 System Integrations")
        
        st.markdown("**CRM Integration**")
        crm_system = st.selectbox("CRM System", ["HubSpot", "Salesforce", "Pipedrive", "Custom API"])
        st.text_input("CRM API Key", type="password")
        
        st.markdown("**Export Options**")
        if st.button("Export All Prospects (CSV)"):
            st.success("Prospects exported to prospects_export.csv")
        if st.button("Export Market Intelligence (PDF)"):
            st.success("Market report generated: market_intelligence.pdf")
        if st.button("Generate API Documentation"):
            st.info("API docs available at /api/docs")

# Main app
def main():
    # Get current page
    page = sidebar_navigation()
    
    # Route to appropriate page
    if page == "🏠 Landing Page":
        landing_page()
    elif page == "📊 Dashboard":
        dashboard_page()
    elif page == "🎯 Prospect Discovery":
        prospect_discovery_page()
    elif page == "🤖 AI Analysis":
        ai_analysis_page()
    elif page == "📈 Market Intelligence":
        st.title("📈 Market Intelligence")
        market_df = generate_market_intelligence()
        competitors_df = generate_competitor_analysis()
        
        # Display market trends and competitor analysis
        st.markdown("### Tourism Market Trends")
        st.dataframe(market_df.tail(30))
        
        st.markdown("### Competitor Analysis")
        st.dataframe(competitors_df)
    elif page == "🔄 Data Collection":
        data_collection_page()
    elif page == "⚙️ Settings":
        settings_page()

if __name__ == "__main__":
    main()