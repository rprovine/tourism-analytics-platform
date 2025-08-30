# 🌺 Tourism Analytics Platform

> **🚀 Live at [analytics.lenilani.com](https://analytics.lenilani.com) - Powered by [Lenilani](https://lenilani.com)**

A comprehensive Streamlit-based analytics dashboard for Hawaii's tourism industry featuring real-time insights, chat analytics, sentiment analysis, lead management, and demand forecasting.

---

**⚡ Enterprise-Grade Tourism Intelligence Platform**  
*Built with cutting-edge AI and machine learning technologies to transform hospitality data into actionable business insights.*

## 🌐 Live Demo

**Production URL:** https://analytics.lenilani.com

## Features

### 🎯 Core Analytics Modules

1. **Overview Dashboard**
   - Key performance metrics and KPIs
   - Real-time visitor trends
   - Engagement statistics
   - Quick insights summary

2. **Chat Analytics**
   - Conversation volume tracking
   - Response time metrics
   - User satisfaction scores
   - Topic analysis and trends

3. **Sentiment Analysis**
   - Real-time sentiment tracking
   - Trend analysis over time
   - Sentiment by source
   - Alert system for negative trends

4. **Lead Management**
   - Lead scoring and tracking
   - Conversion funnel analysis
   - Source attribution
   - ROI metrics

5. **Revenue Analytics**
   - Revenue forecasting
   - Seasonal trend analysis
   - Channel performance
   - Pricing optimization insights

6. **Demand Forecasting**
   - Predictive analytics
   - Seasonal patterns
   - Market trend analysis
   - Capacity planning

7. **Chatbot Simulator**
   - Test conversation flows
   - Simulate user interactions
   - Response optimization
   - Training data generation

8. **API Integration**
   - RESTful API endpoints
   - Data export capabilities
   - Third-party integrations
   - Webhook support

9. **Competitive Analysis**
   - Market positioning
   - Competitor benchmarking
   - SWOT analysis
   - Market share tracking

## Technology Stack

- **Frontend Framework**: Streamlit
- **Data Visualization**: Plotly, Matplotlib
- **Data Processing**: Pandas, NumPy
- **Deployment**: Streamlit Cloud + Vercel
- **Custom Domain**: analytics.lenilani.com
- **Version Control**: Git, GitHub

## 🚀 Deployment

### Production Deployment

The platform is deployed using a combination of Streamlit Cloud and Vercel:

- **Frontend**: Streamlit Cloud (https://tourism-analytics-platform-lenilani.streamlit.app)
- **Custom Domain**: Vercel proxy (https://analytics.lenilani.com)
- **Repository**: https://github.com/rprovine/tourism-analytics-platform

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/rprovine/tourism-analytics-platform.git
cd tourism-analytics-platform
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run streamlit_app.py
```

4. **Access locally:**
```
http://localhost:8501
```

## 📁 Project Structure

```
tourism-analytics-platform/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── public/
│   ├── index.html           # Redirect page
│   └── embed.html           # Embed wrapper
├── vercel.json              # Vercel configuration
├── package.json             # Node.js metadata
├── VERCEL_SETUP.md          # Vercel setup documentation
└── README.md                # This file
```

## 🔧 Configuration

### Streamlit Configuration

The app uses a custom theme defined in `.streamlit/config.toml`:
- Primary Color: `#667eea` (Purple)
- Background: White
- Font: Sans serif

### Vercel Configuration

Custom domain routing is handled through `vercel.json` with:
- Static file serving from `/public`
- Automatic redirect to Streamlit app
- Embed mode for seamless integration

## 📈 Data Sources

Currently using simulated data for demonstration purposes. In production, integrate with:
- Chat platform APIs
- Google Analytics
- CRM systems
- Payment gateways
- Social media APIs

## 🔒 Security

- All data is processed server-side
- No sensitive data stored in browser
- HTTPS encryption enforced
- Environment variables for secrets

## 🎯 Roadmap

- [ ] Real-time data integration
- [ ] Advanced ML models
- [ ] Mobile responsive design
- [ ] Multi-language support
- [ ] Export functionality
- [ ] User authentication
- [ ] Custom dashboards
- [ ] Email alerts

---

## 🏢 About Lenilani

**Lenilani** is a leading technology innovator specializing in AI-powered solutions for Hawaii's tourism and hospitality industry. We transform complex data into actionable insights that drive business growth and enhance visitor experiences.

### Our Expertise
- 🧠 **Artificial Intelligence & Machine Learning**
- 📊 **Advanced Data Analytics & Business Intelligence** 
- 🚀 **Enterprise Software Development**
- 🌺 **Hawaii Tourism Technology Solutions**
- 📱 **Real-time Dashboard & Visualization Platforms**

### Why Choose Lenilani?
- ✅ **Local Expertise** with deep understanding of Hawaii's unique market
- ✅ **Cutting-Edge Technology** using the latest frameworks
- ✅ **Industry Leadership** in tourism analytics
- ✅ **Scalable Architecture** built for growth
- ✅ **Dedicated Support** ensuring continuous operation

**Ready to transform your tourism business with AI?**  
📧 Contact us: [support@lenilani.com](mailto:support@lenilani.com)  
🌐 Visit: [www.lenilani.com](https://lenilani.com)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📝 License

Copyright © 2024 Lenilani. All rights reserved.

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/rprovine/tourism-analytics-platform/issues
- Email: support@lenilani.com

## 🙏 Acknowledgments

Built with Streamlit, deployed on Vercel, and powered by the Hawaii tourism community.

---

**Last Updated:** August 2025  
**Version:** 1.0.0  
**Status:** Production

*© 2024 Lenilani. All rights reserved. This Tourism Analytics Platform represents our commitment to revolutionizing Hawaii's hospitality industry through innovative AI solutions.*