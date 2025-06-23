from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os

from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.core.demo_database import demo_db

router = APIRouter()


@router.get("/sentiment")
async def get_sentiment_dashboard(
    business_id: str = Query("demo", description="Business ID"),
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get sentiment analysis dashboard"""
    try:
        # Use demo data if no database
        if os.getenv("DATABASE_URL") is None:
            reviews = demo_db.get_reviews()
            positive = len([r for r in reviews if r["sentiment"] == "positive"])
            neutral = len([r for r in reviews if r["sentiment"] == "neutral"])
            negative = len([r for r in reviews if r["sentiment"] == "negative"])
            avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
            
            return {
                "sentiment_distribution": {
                    "positive": positive,
                    "neutral": neutral, 
                    "negative": negative
                },
                "average_rating": round(avg_rating, 1),
                "total_reviews": len(reviews),
                "reviews": reviews[:10],  # Latest 10 reviews
                "trends": {
                    "rating_trend": "stable",
                    "sentiment_trend": "positive"
                }
            }
        else:
            dashboard = await DashboardService.get_sentiment_dashboard(db, business_id, days)
            return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_forecast_dashboard(
    business_id: str = Query(..., description="Business ID"),
    forecast_days: int = Query(30, description="Number of days to forecast"),
    db: AsyncSession = Depends(get_db)
):
    """Get demand forecasting dashboard"""
    try:
        dashboard = await DashboardService.get_forecast_dashboard(db, business_id, forecast_days)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat")
async def get_chat_dashboard(
    business_id: str = Query(..., description="Business ID"),
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get chatbot analytics dashboard"""
    try:
        dashboard = await DashboardService.get_chat_dashboard(db, business_id, days)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
async def get_overview_dashboard(
    business_id: str = Query(..., description="Business ID"),
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive overview dashboard"""
    try:
        dashboard = await DashboardService.get_overview_dashboard(db, business_id, days)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_business_metrics(
    business_id: str = Query(..., description="Business ID"),
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get key business metrics"""
    try:
        metrics = await DashboardService.get_business_metrics(db, business_id, days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_dashboard_config(
    business_id: str = Query(..., description="Business ID")
):
    """Get dashboard configuration options"""
    try:
        config = await DashboardService.get_dashboard_config(business_id)
        return {
            "status": "success",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))