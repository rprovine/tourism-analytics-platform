import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from app.core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


class DashboardGenerator:
    def __init__(self):
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#17becf',
            'dark': '#8c564b'
        }
    
    async def generate_sentiment_dashboard(self, sentiment_data: Dict) -> Dict:
        """
        Generate sentiment analysis dashboard
        """
        try:
            cache_key = f"dashboard:sentiment:{hash(str(sentiment_data))}"
            cached_dashboard = await redis_client.get_json(cache_key)
            if cached_dashboard:
                return cached_dashboard
            
            # Sentiment distribution pie chart
            sentiment_dist = sentiment_data.get('sentiment_distribution', {})
            if sentiment_dist:
                sentiment_pie = go.Figure(data=[
                    go.Pie(
                        labels=list(sentiment_dist.keys()),
                        values=list(sentiment_dist.values()),
                        hole=0.3,
                        marker_colors=[self.color_scheme['success'], self.color_scheme['warning'], self.color_scheme['info']]
                    )
                ])
                sentiment_pie.update_layout(
                    title="Sentiment Distribution",
                    showlegend=True,
                    height=400
                )
            else:
                sentiment_pie = None
            
            # Sentiment trend over time
            trend_data = sentiment_data.get('trend_analysis', {}).get('daily_scores', [])
            if trend_data:
                df_trend = pd.DataFrame(trend_data)
                sentiment_trend = go.Figure()
                sentiment_trend.add_trace(go.Scatter(
                    x=df_trend['date'],
                    y=df_trend['avg_sentiment'],
                    mode='lines+markers',
                    name='Average Sentiment',
                    line=dict(color=self.color_scheme['primary'])
                ))
                sentiment_trend.update_layout(
                    title="Sentiment Trend Over Time",
                    xaxis_title="Date",
                    yaxis_title="Average Sentiment Score",
                    height=400
                )
            else:
                sentiment_trend = None
            
            # Top emotions bar chart
            top_emotions = sentiment_data.get('top_emotions', {})
            if top_emotions:
                emotions_bar = go.Figure(data=[
                    go.Bar(
                        x=list(top_emotions.keys()),
                        y=list(top_emotions.values()),
                        marker_color=self.color_scheme['secondary']
                    )
                ])
                emotions_bar.update_layout(
                    title="Top Emotions in Reviews",
                    xaxis_title="Emotion",
                    yaxis_title="Average Score",
                    height=400
                )
            else:
                emotions_bar = None
            
            # Keywords word cloud data
            keywords = sentiment_data.get('common_keywords', [])
            
            dashboard_data = {
                'sentiment_pie': sentiment_pie.to_json() if sentiment_pie else None,
                'sentiment_trend': sentiment_trend.to_json() if sentiment_trend else None,
                'emotions_bar': emotions_bar.to_json() if emotions_bar else None,
                'keywords': keywords,
                'summary_stats': {
                    'total_reviews': sentiment_data.get('total_reviews', 0),
                    'overall_sentiment': sentiment_data.get('overall_sentiment', 'neutral'),
                    'average_score': sentiment_data.get('average_score', 0.0),
                    'trend': sentiment_data.get('trend_analysis', {}).get('trend', 'stable')
                }
            }
            
            # Cache the dashboard
            await redis_client.set_json(cache_key, dashboard_data, expire=1800)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Sentiment dashboard generation error: {e}")
            return {'error': str(e)}
    
    async def generate_demand_forecast_dashboard(self, forecast_data: Dict, historical_data: List[Dict]) -> Dict:
        """
        Generate demand forecasting dashboard
        """
        try:
            cache_key = f"dashboard:forecast:{hash(str(forecast_data))}"
            cached_dashboard = await redis_client.get_json(cache_key)
            if cached_dashboard:
                return cached_dashboard
            
            # Historical vs Predicted chart
            if historical_data and forecast_data.get('predictions'):
                df_historical = pd.DataFrame(historical_data)
                df_forecast = pd.DataFrame(forecast_data['predictions'])
                
                forecast_chart = go.Figure()
                
                # Historical data
                if not df_historical.empty:
                    forecast_chart.add_trace(go.Scatter(
                        x=df_historical['date'],
                        y=df_historical['visitor_count'],
                        mode='lines+markers',
                        name='Historical Data',
                        line=dict(color=self.color_scheme['primary'])
                    ))
                
                # Predicted data
                if not df_forecast.empty:
                    forecast_chart.add_trace(go.Scatter(
                        x=df_forecast['date'],
                        y=df_forecast['predicted_visitors'],
                        mode='lines+markers',
                        name='Predictions',
                        line=dict(color=self.color_scheme['warning'], dash='dash')
                    ))
                    
                    # Confidence intervals
                    forecast_chart.add_trace(go.Scatter(
                        x=df_forecast['date'],
                        y=df_forecast['confidence_upper'],
                        mode='lines',
                        line=dict(width=0),
                        name='Upper Confidence',
                        showlegend=False
                    ))
                    
                    forecast_chart.add_trace(go.Scatter(
                        x=df_forecast['date'],
                        y=df_forecast['confidence_lower'],
                        mode='lines',
                        fill='tonexty',
                        fillcolor='rgba(255, 127, 14, 0.2)',
                        line=dict(width=0),
                        name='Confidence Interval',
                        showlegend=True
                    ))
                
                forecast_chart.update_layout(
                    title="Visitor Demand Forecast",
                    xaxis_title="Date",
                    yaxis_title="Number of Visitors",
                    height=500
                )
            else:
                forecast_chart = None
            
            # Model performance metrics
            performance = forecast_data.get('model_performance', {})
            if performance:
                metrics_bar = go.Figure(data=[
                    go.Bar(
                        x=['MAE', 'RMSE', 'R² Score'],
                        y=[
                            performance.get('mae', 0),
                            performance.get('rmse', 0),
                            performance.get('r2', 0)
                        ],
                        marker_color=[self.color_scheme['success'], self.color_scheme['warning'], self.color_scheme['info']]
                    )
                ])
                metrics_bar.update_layout(
                    title="Model Performance Metrics",
                    yaxis_title="Score",
                    height=400
                )
            else:
                metrics_bar = None
            
            # Seasonal patterns
            if historical_data:
                df_seasonal = pd.DataFrame(historical_data)
                if 'date' in df_seasonal.columns:
                    df_seasonal['date'] = pd.to_datetime(df_seasonal['date'])
                    df_seasonal['month'] = df_seasonal['date'].dt.month
                    df_seasonal['day_of_week'] = df_seasonal['date'].dt.day_name()
                    
                    # Monthly pattern
                    monthly_avg = df_seasonal.groupby('month')['visitor_count'].mean().reset_index()
                    
                    monthly_pattern = go.Figure(data=[
                        go.Bar(
                            x=monthly_avg['month'],
                            y=monthly_avg['visitor_count'],
                            marker_color=self.color_scheme['secondary']
                        )
                    ])
                    monthly_pattern.update_layout(
                        title="Monthly Visitor Patterns",
                        xaxis_title="Month",
                        yaxis_title="Average Visitors",
                        height=400
                    )
                    
                    # Weekly pattern
                    weekly_avg = df_seasonal.groupby('day_of_week')['visitor_count'].mean().reset_index()
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekly_avg['day_of_week'] = pd.Categorical(weekly_avg['day_of_week'], categories=day_order, ordered=True)
                    weekly_avg = weekly_avg.sort_values('day_of_week')
                    
                    weekly_pattern = go.Figure(data=[
                        go.Bar(
                            x=weekly_avg['day_of_week'],
                            y=weekly_avg['visitor_count'],
                            marker_color=self.color_scheme['info']
                        )
                    ])
                    weekly_pattern.update_layout(
                        title="Weekly Visitor Patterns",
                        xaxis_title="Day of Week",
                        yaxis_title="Average Visitors",
                        height=400
                    )
                else:
                    monthly_pattern = None
                    weekly_pattern = None
            else:
                monthly_pattern = None
                weekly_pattern = None
            
            dashboard_data = {
                'forecast_chart': forecast_chart.to_json() if forecast_chart else None,
                'metrics_bar': metrics_bar.to_json() if metrics_bar else None,
                'monthly_pattern': monthly_pattern.to_json() if monthly_pattern else None,
                'weekly_pattern': weekly_pattern.to_json() if weekly_pattern else None,
                'summary_stats': {
                    'total_predictions': len(forecast_data.get('predictions', [])),
                    'model_accuracy': performance.get('r2', 0),
                    'prediction_range': f"{len(forecast_data.get('predictions', []))} days",
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            # Cache the dashboard
            await redis_client.set_json(cache_key, dashboard_data, expire=1800)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Forecast dashboard generation error: {e}")
            return {'error': str(e)}
    
    async def generate_chat_analytics_dashboard(self, chat_analytics: Dict) -> Dict:
        """
        Generate chatbot analytics dashboard
        """
        try:
            cache_key = f"dashboard:chat:{hash(str(chat_analytics))}"
            cached_dashboard = await redis_client.get_json(cache_key)
            if cached_dashboard:
                return cached_dashboard
            
            analytics = chat_analytics.get('analytics', {})
            
            # Intent distribution pie chart
            intent_dist = analytics.get('intent_distribution', {})
            if intent_dist:
                intent_pie = go.Figure(data=[
                    go.Pie(
                        labels=list(intent_dist.keys()),
                        values=list(intent_dist.values()),
                        hole=0.3
                    )
                ])
                intent_pie.update_layout(
                    title="User Intent Distribution",
                    height=400
                )
            else:
                intent_pie = None
            
            # Language distribution bar chart
            language_dist = analytics.get('language_distribution', {})
            if language_dist:
                language_bar = go.Figure(data=[
                    go.Bar(
                        x=list(language_dist.keys()),
                        y=list(language_dist.values()),
                        marker_color=self.color_scheme['primary']
                    )
                ])
                language_bar.update_layout(
                    title="User Language Distribution",
                    xaxis_title="Language",
                    yaxis_title="Number of Messages",
                    height=400
                )
            else:
                language_bar = None
            
            # Response time gauge
            avg_response_time = analytics.get('average_response_time_ms', 0)
            response_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_response_time,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Average Response Time (ms)"},
                delta={'reference': 1000},
                gauge={
                    'axis': {'range': [None, 3000]},
                    'bar': {'color': self.color_scheme['primary']},
                    'steps': [
                        {'range': [0, 1000], 'color': self.color_scheme['success']},
                        {'range': [1000, 2000], 'color': self.color_scheme['warning']},
                        {'range': [2000, 3000], 'color': self.color_scheme['warning']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 2000
                    }
                }
            ))
            response_gauge.update_layout(height=400)
            
            # Rating gauge
            avg_rating = analytics.get('average_rating', 0)
            rating_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_rating,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Average User Rating"},
                gauge={
                    'axis': {'range': [None, 5]},
                    'bar': {'color': self.color_scheme['success']},
                    'steps': [
                        {'range': [0, 2], 'color': self.color_scheme['warning']},
                        {'range': [2, 3.5], 'color': 'yellow'},
                        {'range': [3.5, 5], 'color': self.color_scheme['success']}
                    ]
                }
            ))
            rating_gauge.update_layout(height=400)
            
            dashboard_data = {
                'intent_pie': intent_pie.to_json() if intent_pie else None,
                'language_bar': language_bar.to_json() if language_bar else None,
                'response_gauge': response_gauge.to_json(),
                'rating_gauge': rating_gauge.to_json(),
                'summary_stats': {
                    'total_sessions': analytics.get('total_sessions', 0),
                    'active_sessions': analytics.get('active_sessions', 0),
                    'total_messages': analytics.get('total_messages', 0),
                    'average_confidence': round(analytics.get('average_confidence', 0), 2),
                    'total_feedback': analytics.get('total_feedback', 0)
                }
            }
            
            # Cache the dashboard
            await redis_client.set_json(cache_key, dashboard_data, expire=1800)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Chat analytics dashboard generation error: {e}")
            return {'error': str(e)}
    
    async def generate_overview_dashboard(
        self,
        sentiment_data: Dict,
        forecast_data: Dict,
        chat_analytics: Dict,
        business_metrics: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive overview dashboard
        """
        try:
            # Key metrics cards
            metrics = {
                'sentiment': {
                    'title': 'Overall Sentiment',
                    'value': sentiment_data.get('overall_sentiment', 'neutral').title(),
                    'score': sentiment_data.get('average_score', 0),
                    'change': sentiment_data.get('trend_analysis', {}).get('trend', 'stable')
                },
                'reviews': {
                    'title': 'Total Reviews',
                    'value': sentiment_data.get('total_reviews', 0),
                    'change': '+12%'  # This would come from period comparison
                },
                'chat_sessions': {
                    'title': 'Chat Sessions',
                    'value': chat_analytics.get('analytics', {}).get('total_sessions', 0),
                    'change': chat_analytics.get('analytics', {}).get('active_sessions', 0)
                },
                'forecast_accuracy': {
                    'title': 'Forecast Accuracy',
                    'value': f"{round(forecast_data.get('model_performance', {}).get('r2', 0) * 100, 1)}%",
                    'change': 'improving'
                }
            }
            
            # Create combined trend chart
            combined_chart = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Sentiment Trend', 'Visitor Forecast', 'Chat Volume', 'Revenue Trend'],
                specs=[[{'secondary_y': False}, {'secondary_y': False}],
                       [{'secondary_y': False}, {'secondary_y': False}]]
            )
            
            # Add sentiment trend
            sentiment_trend = sentiment_data.get('trend_analysis', {}).get('daily_scores', [])
            if sentiment_trend:
                df_sentiment = pd.DataFrame(sentiment_trend)
                combined_chart.add_trace(
                    go.Scatter(
                        x=df_sentiment['date'],
                        y=df_sentiment['avg_sentiment'],
                        name='Sentiment',
                        line=dict(color=self.color_scheme['primary'])
                    ),
                    row=1, col=1
                )
            
            # Add forecast data
            predictions = forecast_data.get('predictions', [])
            if predictions:
                df_forecast = pd.DataFrame(predictions[-7:])  # Last 7 days
                combined_chart.add_trace(
                    go.Scatter(
                        x=df_forecast['date'],
                        y=df_forecast['predicted_visitors'],
                        name='Forecast',
                        line=dict(color=self.color_scheme['warning'])
                    ),
                    row=1, col=2
                )
            
            combined_chart.update_layout(
                height=600,
                title_text="Business Overview Dashboard",
                showlegend=True
            )
            
            dashboard_data = {
                'metrics_cards': metrics,
                'overview_chart': combined_chart.to_json(),
                'alerts': self._generate_alerts(sentiment_data, forecast_data, chat_analytics),
                'recommendations': self._generate_recommendations(sentiment_data, forecast_data, chat_analytics),
                'last_updated': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Overview dashboard generation error: {e}")
            return {'error': str(e)}
    
    def _generate_alerts(self, sentiment_data: Dict, forecast_data: Dict, chat_analytics: Dict) -> List[Dict]:
        """
        Generate alerts based on data analysis
        """
        alerts = []
        
        # Sentiment alerts
        avg_sentiment = sentiment_data.get('average_score', 0)
        if avg_sentiment < -0.3:
            alerts.append({
                'type': 'warning',
                'title': 'Negative Sentiment Alert',
                'message': 'Recent reviews show declining sentiment. Consider addressing customer concerns.',
                'priority': 'high'
            })
        
        # Chat response time alert
        avg_response_time = chat_analytics.get('analytics', {}).get('average_response_time_ms', 0)
        if avg_response_time > 2000:
            alerts.append({
                'type': 'info',
                'title': 'Response Time Alert',
                'message': 'Chatbot response time is above 2 seconds. Consider optimization.',
                'priority': 'medium'
            })
        
        # Low confidence in chat
        avg_confidence = chat_analytics.get('analytics', {}).get('average_confidence', 1)
        if avg_confidence < 0.7:
            alerts.append({
                'type': 'warning',
                'title': 'Low Chat Confidence',
                'message': 'Chatbot confidence is low. Consider training with more data.',
                'priority': 'medium'
            })
        
        return alerts
    
    def _generate_recommendations(self, sentiment_data: Dict, forecast_data: Dict, chat_analytics: Dict) -> List[Dict]:
        """
        Generate recommendations based on data analysis
        """
        recommendations = []
        
        # Sentiment recommendations
        negative_sentiment = sentiment_data.get('sentiment_distribution', {}).get('negative', 0)
        total_reviews = sentiment_data.get('total_reviews', 1)
        if negative_sentiment / total_reviews > 0.3:
            recommendations.append({
                'category': 'Customer Experience',
                'title': 'Address Negative Feedback',
                'description': 'Focus on resolving common issues mentioned in negative reviews.',
                'impact': 'high'
            })
        
        # Forecast recommendations
        predictions = forecast_data.get('predictions', [])
        if predictions:
            upcoming_peak = max(predictions[:7], key=lambda x: x.get('predicted_visitors', 0))
            recommendations.append({
                'category': 'Capacity Planning',
                'title': 'Prepare for Peak Demand',
                'description': f"Expected peak of {upcoming_peak.get('predicted_visitors', 0)} visitors on {upcoming_peak.get('date')}",
                'impact': 'medium'
            })
        
        # Chat recommendations
        popular_intents = chat_analytics.get('analytics', {}).get('intent_distribution', {})
        if 'booking' in popular_intents and popular_intents['booking'] > 30:
            recommendations.append({
                'category': 'Automation',
                'title': 'Enhance Booking Process',
                'description': 'Many users ask about bookings. Consider streamlining the booking flow.',
                'impact': 'high'
            })
        
        return recommendations


# Global instance
dashboard_generator = DashboardGenerator()