from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.dashboard.dashboard_generator import dashboard_generator
from app.services.review_service import ReviewService
from app.services.forecasting_service import ForecastingService
from app.services.chat_service import ChatService


class DashboardService:
    
    @staticmethod
    async def get_sentiment_dashboard(
        db: AsyncSession,
        business_id: str,
        days: int = 30
    ) -> Dict:
        """
        Generate sentiment analysis dashboard
        """
        try:
            # Get sentiment analytics data
            sentiment_data = await ReviewService.get_sentiment_analytics(
                db, business_id, days
            )
            
            # Generate dashboard
            dashboard = await dashboard_generator.generate_sentiment_dashboard(sentiment_data)
            
            return {
                'status': 'success',
                'dashboard': dashboard,
                'data_period_days': days,
                'business_id': business_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Sentiment dashboard generation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_forecast_dashboard(
        db: AsyncSession,
        business_id: str,
        forecast_days: int = 30
    ) -> Dict:
        """
        Generate demand forecasting dashboard
        """
        try:
            # Generate forecast data
            forecast_result = await ForecastingService.generate_forecast(
                db, business_id, forecast_days
            )
            
            if forecast_result['status'] != 'success':
                return forecast_result
            
            # Get historical data for comparison
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)  # Last 90 days
            
            historical_data = await ForecastingService.get_tourism_data(
                db, business_id, start_date, end_date
            )
            
            # Convert to dict format
            historical_dict = []
            for record in historical_data:
                historical_dict.append({
                    'date': record.date.isoformat(),
                    'visitor_count': record.visitor_count,
                    'revenue': record.revenue,
                    'bookings': record.bookings
                })
            
            # Generate dashboard
            dashboard = await dashboard_generator.generate_demand_forecast_dashboard(
                forecast_result, historical_dict
            )
            
            return {
                'status': 'success',
                'dashboard': dashboard,
                'forecast_days': forecast_days,
                'business_id': business_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Forecast dashboard generation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_chat_dashboard(
        db: AsyncSession,
        business_id: str,
        days: int = 30
    ) -> Dict:
        """
        Generate chatbot analytics dashboard
        """
        try:
            # Get chat analytics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            chat_analytics = await ChatService.get_chat_analytics(
                db, business_id, start_date, end_date
            )
            
            if chat_analytics['status'] != 'success':
                return chat_analytics
            
            # Generate dashboard
            dashboard = await dashboard_generator.generate_chat_analytics_dashboard(chat_analytics)
            
            return {
                'status': 'success',
                'dashboard': dashboard,
                'data_period_days': days,
                'business_id': business_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Chat dashboard generation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_overview_dashboard(
        db: AsyncSession,
        business_id: str,
        days: int = 30
    ) -> Dict:
        """
        Generate comprehensive overview dashboard
        """
        try:
            # Get all analytics data
            sentiment_data = await ReviewService.get_sentiment_analytics(
                db, business_id, days
            )
            
            forecast_result = await ForecastingService.generate_forecast(
                db, business_id, 7  # Next 7 days for overview
            )
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            chat_analytics = await ChatService.get_chat_analytics(
                db, business_id, start_date, end_date
            )
            
            # Handle potential errors in individual services
            if not isinstance(sentiment_data, dict):
                sentiment_data = {}
            
            if forecast_result.get('status') != 'success':
                forecast_result = {'predictions': [], 'model_performance': {}}
            
            if chat_analytics.get('status') != 'success':
                chat_analytics = {'analytics': {}}
            
            # Generate overview dashboard
            dashboard = await dashboard_generator.generate_overview_dashboard(
                sentiment_data, forecast_result, chat_analytics
            )
            
            return {
                'status': 'success',
                'dashboard': dashboard,
                'data_period_days': days,
                'business_id': business_id,
                'components': {
                    'sentiment_available': bool(sentiment_data),
                    'forecast_available': bool(forecast_result.get('predictions')),
                    'chat_available': bool(chat_analytics.get('analytics'))
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Overview dashboard generation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_business_metrics(
        db: AsyncSession,
        business_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get key business metrics for dashboard
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get review statistics
            review_stats = await ReviewService.get_review_statistics(db, business_id)
            
            # Get chat statistics
            chat_analytics = await ChatService.get_chat_analytics(
                db, business_id, start_date, end_date
            )
            
            # Get forecast accuracy if available
            forecast_accuracy = await ForecastingService.get_forecast_accuracy(
                db, business_id, days
            )
            
            # Get tourism data summary
            tourism_data = await ForecastingService.get_tourism_data(
                db, business_id, start_date, end_date, limit=1000
            )
            
            total_visitors = sum(record.visitor_count for record in tourism_data)
            total_revenue = sum(record.revenue or 0 for record in tourism_data)
            avg_daily_visitors = total_visitors / days if days > 0 else 0
            
            metrics = {
                'reviews': {
                    'total': review_stats.get('total_reviews', 0),
                    'processed': review_stats.get('processed_reviews', 0),
                    'average_rating': review_stats.get('average_rating', 0),
                    'sentiment_distribution': review_stats.get('sentiment_distribution', {})
                },
                'chat': {
                    'total_sessions': chat_analytics.get('analytics', {}).get('total_sessions', 0),
                    'active_sessions': chat_analytics.get('analytics', {}).get('active_sessions', 0),
                    'total_messages': chat_analytics.get('analytics', {}).get('total_messages', 0),
                    'average_rating': chat_analytics.get('analytics', {}).get('average_rating', 0)
                },
                'visitors': {
                    'total_period': total_visitors,
                    'average_daily': round(avg_daily_visitors, 1),
                    'total_revenue': total_revenue,
                    'data_points': len(tourism_data)
                },
                'forecasting': {
                    'accuracy_metrics': forecast_accuracy.get('accuracy_metrics', {}),
                    'model_available': forecast_accuracy.get('status') == 'success'
                },
                'period': {
                    'days': days,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
            return {
                'status': 'success',
                'metrics': metrics,
                'business_id': business_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Metrics calculation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_dashboard_config(business_id: str) -> Dict:
        """
        Get dashboard configuration options
        """
        return {
            'available_dashboards': [
                {
                    'id': 'overview',
                    'name': 'Business Overview',
                    'description': 'Comprehensive view of all business metrics',
                    'features': ['sentiment', 'forecasting', 'chat', 'alerts']
                },
                {
                    'id': 'sentiment',
                    'name': 'Sentiment Analysis',
                    'description': 'Customer sentiment analysis from reviews',
                    'features': ['sentiment_trends', 'emotion_analysis', 'keyword_analysis']
                },
                {
                    'id': 'forecast',
                    'name': 'Demand Forecasting',
                    'description': 'Visitor demand predictions and trends',
                    'features': ['predictions', 'seasonal_patterns', 'model_performance']
                },
                {
                    'id': 'chat',
                    'name': 'Chatbot Analytics',
                    'description': 'Chatbot performance and user interactions',
                    'features': ['intent_analysis', 'language_distribution', 'performance_metrics']
                }
            ],
            'time_periods': [
                {'value': 7, 'label': 'Last 7 days'},
                {'value': 30, 'label': 'Last 30 days'},
                {'value': 90, 'label': 'Last 3 months'},
                {'value': 365, 'label': 'Last year'}
            ],
            'export_formats': ['json', 'pdf', 'png'],
            'refresh_intervals': [
                {'value': 300, 'label': '5 minutes'},
                {'value': 900, 'label': '15 minutes'},
                {'value': 1800, 'label': '30 minutes'},
                {'value': 3600, 'label': '1 hour'}
            ]
        }