from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.services.forecasting_service import ForecastingService

router = APIRouter()


class TourismDataCreate(BaseModel):
    business_id: str
    date: date
    visitor_count: int
    revenue: Optional[float] = None
    bookings: int = 0
    cancellations: int = 0
    occupancy_rate: Optional[float] = None
    average_stay_duration: Optional[float] = None
    source_market: Optional[str] = None
    weather_condition: Optional[str] = None
    temperature: Optional[float] = None
    is_holiday: bool = False
    is_weekend: bool = False
    special_event: Optional[str] = None
    marketing_spend: Optional[float] = None


class ForecastRequest(BaseModel):
    business_id: str
    days_ahead: int = 30
    base_conditions: Optional[dict] = None


@router.post("/data")
async def add_tourism_data(
    data: TourismDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add tourism data point"""
    try:
        record = await ForecastingService.add_tourism_data(db, data.dict())
        return {
            "status": "success",
            "message": "Tourism data added successfully",
            "record_id": record.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/bulk")
async def add_bulk_tourism_data(
    data_list: List[TourismDataCreate],
    db: AsyncSession = Depends(get_db)
):
    """Add multiple tourism data points"""
    try:
        data_dicts = [data.dict() for data in data_list]
        count = await ForecastingService.bulk_add_tourism_data(db, data_dicts)
        return {
            "status": "success",
            "message": f"Added {count} tourism data records",
            "records_added": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data")
async def get_tourism_data(
    business_id: str = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(1000, le=5000),
    db: AsyncSession = Depends(get_db)
):
    """Get historical tourism data"""
    try:
        data = await ForecastingService.get_tourism_data(
            db, business_id, start_date, end_date, limit
        )
        
        return {
            "status": "success",
            "data": [
                {
                    "id": record.id,
                    "business_id": record.business_id,
                    "date": record.date.isoformat(),
                    "visitor_count": record.visitor_count,
                    "revenue": record.revenue,
                    "bookings": record.bookings,
                    "cancellations": record.cancellations,
                    "occupancy_rate": record.occupancy_rate,
                    "average_stay_duration": record.average_stay_duration,
                    "source_market": record.source_market,
                    "weather_condition": record.weather_condition,
                    "temperature": record.temperature,
                    "is_holiday": record.is_holiday,
                    "is_weekend": record.is_weekend,
                    "special_event": record.special_event,
                    "marketing_spend": record.marketing_spend,
                    "created_at": record.created_at
                }
                for record in data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_forecasting_models(
    business_id: Optional[str] = Query(None, description="Business ID (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """Train forecasting models with historical data"""
    try:
        result = await ForecastingService.train_models(db, business_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast")
async def generate_forecast(
    forecast_request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate demand forecast"""
    try:
        result = await ForecastingService.generate_forecast(
            db=db,
            business_id=forecast_request.business_id,
            days_ahead=forecast_request.days_ahead,
            base_conditions=forecast_request.base_conditions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/history")
async def get_forecast_history(
    business_id: str = Query(..., description="Business ID"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical forecast results"""
    try:
        forecasts = await ForecastingService.get_historical_forecasts(
            db, business_id, start_date, end_date
        )
        
        return {
            "status": "success",
            "forecasts": [
                {
                    "id": forecast.id,
                    "business_id": forecast.business_id,
                    "forecast_date": forecast.forecast_date.isoformat(),
                    "predicted_visitors": forecast.predicted_visitors,
                    "predicted_revenue": forecast.predicted_revenue,
                    "predicted_bookings": forecast.predicted_bookings,
                    "confidence_interval_lower": forecast.confidence_interval_lower,
                    "confidence_interval_upper": forecast.confidence_interval_upper,
                    "model_name": forecast.model_name,
                    "model_version": forecast.model_version,
                    "created_at": forecast.created_at
                }
                for forecast in forecasts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accuracy")
async def get_forecast_accuracy(
    business_id: str = Query(..., description="Business ID"),
    days_back: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get forecast accuracy metrics"""
    try:
        accuracy = await ForecastingService.get_forecast_accuracy(db, business_id, days_back)
        return accuracy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/performance")
async def get_model_performance(db: AsyncSession = Depends(get_db)):
    """Get model performance metrics"""
    try:
        performance = await ForecastingService.get_model_performance(db)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))