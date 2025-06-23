from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, date, timedelta
import asyncio

from app.models.tourism_data import TourismData, ForecastResult
from app.analytics.demand_forecaster import demand_forecaster


class ForecastingService:
    
    @staticmethod
    async def train_models(db: AsyncSession, business_id: Optional[str] = None) -> Dict:
        """
        Train forecasting models with historical tourism data
        """
        try:
            # Get historical data
            query = select(TourismData)
            if business_id:
                query = query.where(TourismData.business_id == business_id)
            
            # Only use data from the last 2 years for training
            cutoff_date = datetime.now().date() - timedelta(days=730)
            query = query.where(TourismData.date >= cutoff_date)
            query = query.order_by(TourismData.date)
            
            result = await db.execute(query)
            tourism_records = result.scalars().all()
            
            if not tourism_records:
                return {
                    'status': 'error',
                    'message': 'No historical data available for training'
                }
            
            # Convert to dictionaries
            training_data = []
            for record in tourism_records:
                data_dict = {
                    'business_id': record.business_id,
                    'date': record.date,
                    'visitor_count': record.visitor_count,
                    'revenue': record.revenue or 0,
                    'bookings': record.bookings,
                    'cancellations': record.cancellations,
                    'occupancy_rate': record.occupancy_rate or 0,
                    'average_stay_duration': record.average_stay_duration or 0,
                    'source_market': record.source_market or 'unknown',
                    'weather_condition': record.weather_condition or 'unknown',
                    'temperature': record.temperature or 20.0,
                    'is_holiday': record.is_holiday,
                    'is_weekend': record.is_weekend,
                    'special_event': record.special_event or 'none',
                    'marketing_spend': record.marketing_spend or 0.0
                }
                training_data.append(data_dict)
            
            # Train the models
            training_result = await asyncio.to_thread(
                demand_forecaster.train, 
                training_data
            )
            
            return training_result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Training failed: {str(e)}'
            }
    
    @staticmethod
    async def generate_forecast(
        db: AsyncSession,
        business_id: str,
        days_ahead: int = 30,
        base_conditions: Optional[Dict] = None
    ) -> Dict:
        """
        Generate forecast for future demand
        """
        try:
            # Generate forecast
            forecast_result = await asyncio.to_thread(
                demand_forecaster.forecast_future,
                business_id,
                days_ahead,
                base_conditions
            )
            
            if forecast_result['status'] != 'success':
                return forecast_result
            
            # Save forecast results to database
            saved_forecasts = []
            for prediction in forecast_result['predictions']:
                forecast_record = ForecastResult(
                    business_id=prediction['business_id'],
                    forecast_date=prediction['date'],
                    predicted_visitors=prediction['predicted_visitors'],
                    confidence_interval_lower=prediction['confidence_lower'],
                    confidence_interval_upper=prediction['confidence_upper'],
                    model_name=prediction['model_used'],
                    model_version='1.0'
                )
                db.add(forecast_record)
                saved_forecasts.append(forecast_record)
            
            await db.commit()
            
            return {
                'status': 'success',
                'predictions': forecast_result['predictions'],
                'saved_records': len(saved_forecasts),
                'model_performance': forecast_result.get('model_performance', {})
            }
            
        except Exception as e:
            await db.rollback()
            return {
                'status': 'error',
                'message': f'Forecast generation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_historical_forecasts(
        db: AsyncSession,
        business_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ForecastResult]:
        """
        Get historical forecast results
        """
        query = select(ForecastResult).where(ForecastResult.business_id == business_id)
        
        if start_date:
            query = query.where(ForecastResult.forecast_date >= start_date)
        
        if end_date:
            query = query.where(ForecastResult.forecast_date <= end_date)
        
        query = query.order_by(ForecastResult.forecast_date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def add_tourism_data(db: AsyncSession, data: Dict) -> TourismData:
        """
        Add new tourism data point
        """
        tourism_record = TourismData(**data)
        db.add(tourism_record)
        await db.commit()
        await db.refresh(tourism_record)
        return tourism_record
    
    @staticmethod
    async def bulk_add_tourism_data(db: AsyncSession, data_list: List[Dict]) -> int:
        """
        Add multiple tourism data points
        """
        records = [TourismData(**data) for data in data_list]
        db.add_all(records)
        await db.commit()
        return len(records)
    
    @staticmethod
    async def get_tourism_data(
        db: AsyncSession,
        business_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000
    ) -> List[TourismData]:
        """
        Get historical tourism data
        """
        query = select(TourismData).where(TourismData.business_id == business_id)
        
        if start_date:
            query = query.where(TourismData.date >= start_date)
        
        if end_date:
            query = query.where(TourismData.date <= end_date)
        
        query = query.order_by(TourismData.date.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_forecast_accuracy(
        db: AsyncSession,
        business_id: str,
        days_back: int = 30
    ) -> Dict:
        """
        Calculate forecast accuracy by comparing predictions with actual data
        """
        try:
            # Get actual data from the specified period
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            actual_query = select(TourismData).where(
                and_(
                    TourismData.business_id == business_id,
                    TourismData.date >= start_date,
                    TourismData.date <= end_date
                )
            )
            actual_result = await db.execute(actual_query)
            actual_data = {record.date: record.visitor_count for record in actual_result.scalars().all()}
            
            # Get forecast data for the same period
            forecast_query = select(ForecastResult).where(
                and_(
                    ForecastResult.business_id == business_id,
                    ForecastResult.forecast_date >= start_date,
                    ForecastResult.forecast_date <= end_date
                )
            )
            forecast_result = await db.execute(forecast_query)
            forecast_data = {record.forecast_date: record.predicted_visitors for record in forecast_result.scalars().all()}
            
            # Calculate accuracy metrics
            common_dates = set(actual_data.keys()) & set(forecast_data.keys())
            
            if not common_dates:
                return {
                    'status': 'error',
                    'message': 'No overlapping dates between actual and forecast data'
                }
            
            errors = []
            for date_key in common_dates:
                actual = actual_data[date_key]
                predicted = forecast_data[date_key]
                error = abs(actual - predicted)
                relative_error = error / max(actual, 1) * 100  # Avoid division by zero
                errors.append({
                    'date': date_key,
                    'actual': actual,
                    'predicted': predicted,
                    'absolute_error': error,
                    'relative_error': relative_error
                })
            
            # Calculate summary statistics
            mae = sum(e['absolute_error'] for e in errors) / len(errors)
            mape = sum(e['relative_error'] for e in errors) / len(errors)
            rmse = (sum(e['absolute_error'] ** 2 for e in errors) / len(errors)) ** 0.5
            
            return {
                'status': 'success',
                'accuracy_metrics': {
                    'mean_absolute_error': round(mae, 2),
                    'mean_absolute_percentage_error': round(mape, 2),
                    'root_mean_square_error': round(rmse, 2),
                    'data_points': len(errors)
                },
                'detailed_errors': errors
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Accuracy calculation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_model_performance(db: AsyncSession) -> Dict:
        """
        Get current model performance metrics
        """
        try:
            feature_importance = await asyncio.to_thread(
                demand_forecaster.get_feature_importance
            )
            
            performance_data = {
                'model_status': 'trained' if demand_forecaster.is_trained else 'not_trained',
                'available_models': list(demand_forecaster.models.keys()),
                'performance_metrics': demand_forecaster.model_performance,
                'feature_importance': feature_importance
            }
            
            return {
                'status': 'success',
                'data': performance_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Performance retrieval failed: {str(e)}'
            }