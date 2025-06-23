#!/usr/bin/env python3
"""
Tourism Analytics Platform - Interactive Demo
Demonstrates all features with Hawaiian hotel data
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

class TourismAnalyticsDemo:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.business_id = "aloha_resort_waikiki"  # Main demo hotel
    
    async def close(self):
        await self.client.aclose()
    
    def print_header(self, title: str):
        print("\n" + "="*60)
        print(f"🌺 {title}")
        print("="*60)
    
    def print_section(self, title: str):
        print(f"\n📊 {title}")
        print("-" * 40)
    
    async def demo_health_check(self):
        """Demonstrate health check functionality"""
        self.print_header("HEALTH CHECK & SYSTEM STATUS")
        
        try:
            # Basic health check
            response = await self.client.get(f"{BASE_URL}/health/")
            if response.status_code == 200:
                print("✅ API Status: HEALTHY")
                data = response.json()
                print(f"   Service: {data['service']}")
                print(f"   Version: {data['version']}")
            
            # Detailed health check
            response = await self.client.get(f"{BASE_URL}/health/detailed")
            if response.status_code == 200:
                data = response.json()
                print(f"\n🔍 Detailed Health Check:")
                for service, status in data.get('checks', {}).items():
                    status_icon = "✅" if status['status'] == 'healthy' else "❌"
                    print(f"   {status_icon} {service.title()}: {status['status']}")
                    
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    async def demo_sentiment_analysis(self):
        """Demonstrate sentiment analysis features"""
        self.print_header("SENTIMENT ANALYSIS - CUSTOMER REVIEWS")
        
        try:
            # Get review statistics
            response = await self.client.get(f"{BASE_URL}/reviews/statistics", 
                                           params={"business_id": self.business_id})
            
            if response.status_code == 200:
                stats = response.json()['statistics']
                self.print_section("Review Statistics")
                print(f"📈 Total Reviews: {stats['total_reviews']}")
                print(f"📊 Processed Reviews: {stats['processed_reviews']}")
                print(f"⭐ Average Rating: {stats['average_rating']}/5.0")
                
                sentiment_dist = stats['sentiment_distribution']
                print(f"\n💭 Sentiment Distribution:")
                print(f"   😊 Positive: {sentiment_dist.get('positive', 0)} reviews")
                print(f"   😐 Neutral: {sentiment_dist.get('neutral', 0)} reviews")
                print(f"   😞 Negative: {sentiment_dist.get('negative', 0)} reviews")
            
            # Get detailed sentiment analytics
            response = await self.client.get(f"{BASE_URL}/reviews/analytics",
                                           params={"business_id": self.business_id, "days": 30})
            
            if response.status_code == 200:
                analytics = response.json()['analytics']
                self.print_section("Sentiment Analytics (Last 30 Days)")
                print(f"🎯 Overall Sentiment: {analytics['overall_sentiment'].title()}")
                print(f"📊 Average Score: {analytics['average_score']:.3f}")
                print(f"📈 Trend: {analytics['trend_analysis']['trend'].title()}")
                
                # Top emotions
                if analytics.get('top_emotions'):
                    print(f"\n🎭 Top Emotions Detected:")
                    for emotion, score in list(analytics['top_emotions'].items())[:3]:
                        print(f"   {emotion.title()}: {score:.3f}")
                
                # Common keywords
                if analytics.get('common_keywords'):
                    print(f"\n🔍 Common Keywords:")
                    keywords = analytics['common_keywords'][:8]
                    print(f"   {', '.join(keywords)}")
            
            # Show recent reviews
            response = await self.client.get(f"{BASE_URL}/reviews/",
                                           params={"business_id": self.business_id, "limit": 3})
            
            if response.status_code == 200:
                reviews = response.json()
                self.print_section("Recent Reviews Sample")
                
                for i, review in enumerate(reviews[:3], 1):
                    sentiment_emoji = "😊" if review['sentiment_label'] == 'positive' else "😞" if review['sentiment_label'] == 'negative' else "😐"
                    print(f"\n   Review {i}: {sentiment_emoji} {review['sentiment_label'].title()}")
                    print(f"   Rating: {review['rating']}⭐")
                    print(f"   Text: \"{review['review_text'][:100]}...\"")
                    print(f"   Sentiment Score: {review['sentiment_score']:.3f}")
                    
        except Exception as e:
            print(f"❌ Sentiment analysis demo failed: {e}")
    
    async def demo_demand_forecasting(self):
        """Demonstrate demand forecasting features"""
        self.print_header("DEMAND FORECASTING - VISITOR PREDICTIONS")
        
        try:
            # Get model performance
            response = await self.client.get(f"{BASE_URL}/forecasting/model/performance")
            
            if response.status_code == 200:
                performance = response.json()
                self.print_section("Model Performance")
                
                if performance['status'] == 'success':
                    data = performance['data']
                    print(f"🤖 Model Status: {data['model_status'].title()}")
                    print(f"📊 Available Models: {', '.join(data['available_models'])}")
                    
                    if data.get('performance_metrics'):
                        print(f"\n📈 Performance Metrics:")
                        for model, metrics in data['performance_metrics'].items():
                            print(f"   {model.title()}: R² Score = {metrics.get('r2', 0):.3f}")
            
            # Generate forecast
            forecast_request = {
                "business_id": self.business_id,
                "days_ahead": 14
            }
            
            response = await self.client.post(f"{BASE_URL}/forecasting/forecast", json=forecast_request)
            
            if response.status_code == 200:
                forecast = response.json()
                self.print_section("14-Day Visitor Forecast")
                
                if forecast['status'] == 'success':
                    predictions = forecast['predictions'][:7]  # Show first week
                    print(f"📅 Next 7 Days Forecast:")
                    
                    for pred in predictions:
                        date_str = pred['date']
                        visitors = int(pred['predicted_visitors'])
                        confidence_lower = int(pred['confidence_lower'])
                        confidence_upper = int(pred['confidence_upper'])
                        
                        print(f"   {date_str}: {visitors} visitors ({confidence_lower}-{confidence_upper})")
                    
                    total_predicted = sum(int(p['predicted_visitors']) for p in predictions)
                    print(f"\n📊 Total Week Forecast: {total_predicted} visitors")
            
            # Get historical data summary
            response = await self.client.get(f"{BASE_URL}/forecasting/data",
                                           params={"business_id": self.business_id, "limit": 30})
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']:
                    historical = data['data']
                    self.print_section("Recent Historical Data")
                    
                    total_visitors = sum(record['visitor_count'] for record in historical)
                    avg_visitors = total_visitors / len(historical)
                    total_revenue = sum(record['revenue'] or 0 for record in historical)
                    
                    print(f"📈 Last 30 Days Summary:")
                    print(f"   Total Visitors: {total_visitors}")
                    print(f"   Average Daily: {avg_visitors:.1f}")
                    print(f"   Total Revenue: ${total_revenue:,.2f}")
                    
        except Exception as e:
            print(f"❌ Forecasting demo failed: {e}")
    
    async def demo_chatbot(self):
        """Demonstrate chatbot functionality"""
        self.print_header("MULTILINGUAL CHATBOT - TOURIST INQUIRIES")
        
        try:
            # Get chat analytics
            response = await self.client.get(f"{BASE_URL}/chat/analytics",
                                           params={"business_id": self.business_id})
            
            if response.status_code == 200:
                analytics = response.json()
                if analytics['status'] == 'success':
                    data = analytics['analytics']
                    self.print_section("Chat Analytics Summary")
                    
                    print(f"💬 Total Sessions: {data['total_sessions']}")
                    print(f"🔄 Active Sessions: {data['active_sessions']}")
                    print(f"📨 Total Messages: {data['total_messages']}")
                    print(f"⚡ Avg Response Time: {data['average_response_time_ms']:.0f}ms")
                    print(f"⭐ Average Rating: {data['average_rating']:.1f}/5.0")
                    
                    # Intent distribution
                    if data.get('intent_distribution'):
                        self.print_section("Popular User Intents")
                        intents = data['intent_distribution']
                        for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True)[:5]:
                            print(f"   {intent.title()}: {count} messages")
                    
                    # Language distribution
                    if data.get('language_distribution'):
                        self.print_section("Language Usage")
                        languages = data['language_distribution']
                        for lang, count in languages.items():
                            lang_name = {"en": "English", "es": "Spanish", "fr": "French"}.get(lang, lang)
                            print(f"   {lang_name}: {count} messages")
            
            # Demonstrate a live chat session
            self.print_section("Live Chat Demonstration")
            
            # Create new chat session
            session_data = {
                "business_id": self.business_id,
                "language": "en"
            }
            
            response = await self.client.post(f"{BASE_URL}/chat/session", json=session_data)
            if response.status_code == 200:
                session_id = response.json()["session_id"]
                print(f"✅ Created demo chat session: {session_id[:8]}...")
                
                # Demo conversation
                demo_messages = [
                    "Hi! I'm interested in booking a room for my honeymoon",
                    "We're looking for something romantic with an ocean view",
                    "What dates do you have available in September?",
                    "Perfect! What's included in the honeymoon package?"
                ]
                
                print("\n🗨️  Demo Conversation:")
                
                for i, user_msg in enumerate(demo_messages, 1):
                    print(f"\n   👤 User: {user_msg}")
                    
                    message_data = {
                        "session_id": session_id,
                        "message": user_msg,
                        "business_id": self.business_id
                    }
                    
                    response = await self.client.post(f"{BASE_URL}/chat/message", json=message_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result['status'] == 'success':
                            print(f"   🤖 Bot: {result['response']}")
                            print(f"       Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
                        else:
                            print(f"   🤖 Bot: [Error in response]")
                    
                    await asyncio.sleep(1)  # Simulate conversation pace
                
                # Add feedback
                feedback_data = {
                    "session_id": session_id,
                    "rating": 5,
                    "feedback_text": "Very helpful and quick responses!"
                }
                
                await self.client.post(f"{BASE_URL}/chat/feedback", json=feedback_data)
                print(f"\n   ⭐ User left 5-star feedback!")
                
        except Exception as e:
            print(f"❌ Chatbot demo failed: {e}")
    
    async def demo_lead_management(self):
        """Demonstrate lead management and CRM features"""
        self.print_header("LEAD MANAGEMENT - CRM INTEGRATION")
        
        try:
            # Get lead analytics
            response = await self.client.get(f"{BASE_URL}/leads/analytics/{self.business_id}")
            
            if response.status_code == 200:
                analytics = response.json()
                if analytics['status'] == 'success':
                    data = analytics['analytics']
                    self.print_section("Lead Analytics Summary")
                    
                    print(f"👥 Total Leads: {data['total_leads']}")
                    print(f"✅ Converted Leads: {data['converted_leads']}")
                    print(f"📈 Conversion Rate: {data['conversion_rate']:.1f}%")
                    print(f"💰 Total Conversion Value: ${data['total_conversion_value']:,.2f}")
                    print(f"🎯 Average Lead Score: {data['average_lead_score']:.1f}")
                    
                    # Lead status distribution
                    if data.get('status_distribution'):
                        self.print_section("Lead Status Distribution")
                        for status, count in data['status_distribution'].items():
                            print(f"   {status.title()}: {count} leads")
                    
                    # Lead source distribution
                    if data.get('source_distribution'):
                        self.print_section("Lead Source Distribution")
                        for source, count in data['source_distribution'].items():
                            source_name = source.replace('_', ' ').title() if source else 'Unknown'
                            print(f"   {source_name}: {count} leads")
            
            # Show recent leads
            response = await self.client.get(f"{BASE_URL}/leads/",
                                           params={"business_id": self.business_id, "limit": 5})
            
            if response.status_code == 200:
                leads_data = response.json()
                if leads_data['status'] == 'success':
                    leads = leads_data['leads']
                    self.print_section("Recent Leads Sample")
                    
                    for i, lead in enumerate(leads[:3], 1):
                        status_icon = "✅" if lead['converted'] else "🔄" if lead['lead_status'] == 'qualified' else "📝"
                        print(f"\n   Lead {i}: {status_icon} {lead['first_name']} {lead['last_name']}")
                        print(f"   Email: {lead['email']}")
                        print(f"   Status: {lead['lead_status'].title()}")
                        print(f"   Score: {lead['lead_score']}/100")
                        print(f"   Travel: {lead['travel_dates'] or 'Not specified'}")
                        print(f"   Party Size: {lead['party_size'] or 'Not specified'}")
                        
                        if lead['converted']:
                            print(f"   💰 Conversion Value: ${lead['conversion_value']:,.2f}")
            
            # Demonstrate creating a new lead
            self.print_section("Creating New Demo Lead")
            
            new_lead = {
                "business_id": self.business_id,
                "email": f"demo.lead.{datetime.now().strftime('%H%M%S')}@email.com",
                "first_name": "Alex",
                "last_name": "Demo",
                "phone": "+1-555-DEMO",
                "lead_source": "website",
                "travel_dates": "2024-09-15 to 2024-09-22",
                "destination": "Honolulu",
                "party_size": 2,
                "budget_range": "$4000-6000",
                "service_interests": ["accommodation", "activities", "dining"],
                "interest_level": "hot",
                "notes": "Interested in romantic getaway package"
            }
            
            response = await self.client.post(f"{BASE_URL}/leads/", 
                                            json=new_lead, 
                                            params={"sync_to_hubspot": False})
            
            if response.status_code == 200:
                result = response.json()
                lead_id = result['lead_id']
                print(f"✅ Created demo lead: ID {lead_id}")
                
                # Add activity to the lead
                activity = {
                    "activity_type": "email",
                    "subject": "Welcome and Travel Consultation",
                    "description": "Sent personalized welcome email with Hawaii travel guide",
                    "activity_date": datetime.now().isoformat(),
                    "outcome": "sent"
                }
                
                response = await self.client.post(f"{BASE_URL}/leads/{lead_id}/activities",
                                                json=activity,
                                                params={"sync_to_hubspot": False})
                
                if response.status_code == 200:
                    print(f"✅ Added email activity to lead")
                
                print(f"📧 Lead management workflow demonstrated!")
                
        except Exception as e:
            print(f"❌ Lead management demo failed: {e}")
    
    async def demo_dashboards(self):
        """Demonstrate dashboard and visualization features"""
        self.print_header("BUSINESS INSIGHTS DASHBOARD")
        
        try:
            # Get overview dashboard
            response = await self.client.get(f"{BASE_URL}/dashboard/overview",
                                           params={"business_id": self.business_id, "days": 30})
            
            if response.status_code == 200:
                dashboard = response.json()
                if dashboard['status'] == 'success':
                    data = dashboard['dashboard']
                    
                    self.print_section("Dashboard Overview (Last 30 Days)")
                    
                    # Key metrics
                    if data.get('metrics_cards'):
                        metrics = data['metrics_cards']
                        print(f"📊 Key Performance Indicators:")
                        for metric_name, metric_data in metrics.items():
                            title = metric_data['title']
                            value = metric_data['value']
                            change = metric_data.get('change', '')
                            print(f"   {title}: {value} {change}")
                    
                    # Alerts
                    if data.get('alerts'):
                        self.print_section("System Alerts")
                        for alert in data['alerts']:
                            alert_icon = "🚨" if alert['priority'] == 'high' else "⚠️" if alert['priority'] == 'medium' else "ℹ️"
                            print(f"   {alert_icon} {alert['title']}")
                            print(f"      {alert['message']}")
                    
                    # Recommendations
                    if data.get('recommendations'):
                        self.print_section("AI-Generated Recommendations")
                        for rec in data['recommendations']:
                            impact_icon = "🚀" if rec['impact'] == 'high' else "📈" if rec['impact'] == 'medium' else "💡"
                            print(f"   {impact_icon} {rec['title']} ({rec['category']})")
                            print(f"      {rec['description']}")
            
            # Get business metrics
            response = await self.client.get(f"{BASE_URL}/dashboard/metrics",
                                           params={"business_id": self.business_id, "days": 30})
            
            if response.status_code == 200:
                metrics_data = response.json()
                if metrics_data['status'] == 'success':
                    metrics = metrics_data['metrics']
                    
                    self.print_section("Detailed Business Metrics")
                    
                    # Review metrics
                    reviews = metrics['reviews']
                    print(f"📝 Reviews & Sentiment:")
                    print(f"   Total Reviews: {reviews['total']}")
                    print(f"   Average Rating: {reviews['average_rating']}/5.0")
                    
                    # Chat metrics  
                    chat = metrics['chat']
                    print(f"\n💬 Chat Performance:")
                    print(f"   Total Sessions: {chat['total_sessions']}")
                    print(f"   User Satisfaction: {chat['average_rating']:.1f}/5.0")
                    
                    # Visitor metrics
                    visitors = metrics['visitors']
                    print(f"\n👥 Visitor Analytics:")
                    print(f"   Total Visitors (30d): {visitors['total_period']}")
                    print(f"   Daily Average: {visitors['average_daily']:.1f}")
                    print(f"   Total Revenue: ${visitors['total_revenue']:,.2f}")
                    
                    # Forecasting metrics
                    forecasting = metrics['forecasting']
                    if forecasting['model_available']:
                        accuracy = forecasting['accuracy_metrics']
                        print(f"\n🔮 Forecasting Accuracy:")
                        print(f"   MAPE: {accuracy.get('mean_absolute_percentage_error', 0):.1f}%")
                        print(f"   Data Points: {accuracy.get('data_points', 0)}")
            
            # Show available dashboard types
            response = await self.client.get(f"{BASE_URL}/dashboard/config",
                                           params={"business_id": self.business_id})
            
            if response.status_code == 200:
                config = response.json()['config']
                self.print_section("Available Dashboard Types")
                
                for dashboard_type in config['available_dashboards']:
                    print(f"   📊 {dashboard_type['name']}: {dashboard_type['description']}")
                    print(f"      Features: {', '.join(dashboard_type['features'])}")
                
        except Exception as e:
            print(f"❌ Dashboard demo failed: {e}")
    
    async def demo_summary(self):
        """Show demo summary and next steps"""
        self.print_header("DEMO SUMMARY & NEXT STEPS")
        
        print("🎉 Congratulations! You've seen the Tourism Analytics Platform in action.")
        print("\n📋 What we demonstrated:")
        print("   ✅ Real-time sentiment analysis of customer reviews")
        print("   ✅ AI-powered demand forecasting with ML models")
        print("   ✅ Multilingual chatbot for customer inquiries")
        print("   ✅ Lead management with CRM integration capabilities")
        print("   ✅ Interactive business intelligence dashboards")
        
        print("\n🚀 Next Steps:")
        print("   1. Explore the interactive API docs: http://localhost:8000/docs")
        print("   2. Try different endpoints with your own data")
        print("   3. Configure external APIs (OpenAI, HubSpot, Google Translate)")
        print("   4. Customize the analytics for your specific business needs")
        print("   5. Set up production deployment with real data")
        
        print("\n🔗 Useful URLs:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Health Check: http://localhost:8000/api/v1/health/")
        print("   • Alternative Docs: http://localhost:8000/redoc")
        
        print("\n💡 Pro Tips:")
        print("   • Use the Swagger UI to test endpoints interactively")
        print("   • Check the logs for detailed API responses")
        print("   • The platform supports multiple businesses simultaneously")
        print("   • All analytics update in real-time as new data is added")

async def main():
    """Run the complete demo"""
    demo = TourismAnalyticsDemo()
    
    try:
        print("🌺 Welcome to the Tourism Analytics Platform Demo!")
        print("   This demo showcases Hawaiian hotel analytics capabilities")
        print("   Make sure your platform is running at http://localhost:8000")
        
        # Run all demo sections
        await demo.demo_health_check()
        await demo.demo_sentiment_analysis()
        await demo.demo_demand_forecasting()
        await demo.demo_chatbot()
        await demo.demo_lead_management() 
        await demo.demo_dashboards()
        await demo.demo_summary()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("   Make sure the platform is running: docker-compose up")
    finally:
        await demo.close()

if __name__ == "__main__":
    asyncio.run(main())