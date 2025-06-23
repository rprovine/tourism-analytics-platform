from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.services.review_service import ReviewService

router = APIRouter()


class ReviewCreate(BaseModel):
    business_id: str
    reviewer_name: Optional[str] = None
    reviewer_email: Optional[str] = None
    rating: float
    review_text: str
    language: str = "en"
    source: Optional[str] = None
    source_url: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    business_id: str
    reviewer_name: Optional[str]
    rating: float
    review_text: str
    language: str
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    processed: bool
    created_at: datetime


@router.post("/", response_model=dict)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new review"""
    try:
        # Create review
        review_data = review.dict()
        new_review = await ReviewService.create_review(db, review_data)
        
        # Process sentiment analysis
        processed_review = await ReviewService.process_review_sentiment(db, new_review.id)
        
        return {
            "status": "success",
            "message": "Review created and processed successfully",
            "review_id": processed_review.id,
            "sentiment": {
                "score": processed_review.sentiment_score,
                "label": processed_review.sentiment_label
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[dict])
async def get_reviews(
    business_id: str = Query(..., description="Business ID"),
    sentiment_label: Optional[str] = Query(None, description="Filter by sentiment"),
    min_rating: Optional[float] = Query(None, description="Minimum rating"),
    max_rating: Optional[float] = Query(None, description="Maximum rating"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews with optional filters"""
    try:
        reviews = await ReviewService.get_reviews(
            db=db,
            business_id=business_id,
            sentiment_label=sentiment_label,
            min_rating=min_rating,
            max_rating=max_rating,
            limit=limit,
            offset=offset
        )
        
        return [
            {
                "id": review.id,
                "business_id": review.business_id,
                "reviewer_name": review.reviewer_name,
                "rating": review.rating,
                "review_text": review.review_text,
                "language": review.language,
                "sentiment_score": review.sentiment_score,
                "sentiment_label": review.sentiment_label,
                "processed": review.processed,
                "created_at": review.created_at
            }
            for review in reviews
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_sentiment_analytics(
    business_id: str = Query(..., description="Business ID"),
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get sentiment analytics for reviews"""
    try:
        analytics = await ReviewService.get_sentiment_analytics(db, business_id, days)
        return {
            "status": "success",
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_review_statistics(
    business_id: str = Query(..., description="Business ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get review statistics"""
    try:
        stats = await ReviewService.get_review_statistics(db, business_id)
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-batch")
async def process_unprocessed_reviews(
    business_id: str = Query(..., description="Business ID"),
    limit: int = Query(50, description="Maximum number of reviews to process"),
    db: AsyncSession = Depends(get_db)
):
    """Process sentiment analysis for unprocessed reviews"""
    try:
        processed_count = await ReviewService.bulk_process_unprocessed_reviews(db, limit)
        return {
            "status": "success",
            "message": f"Processed {processed_count} reviews",
            "processed_count": processed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}/sentiment")
async def get_review_sentiment(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed sentiment analysis for a specific review"""
    try:
        # Process sentiment if not already done
        review = await ReviewService.process_review_sentiment(db, review_id)
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {
            "status": "success",
            "review_id": review.id,
            "sentiment": {
                "score": review.sentiment_score,
                "label": review.sentiment_label,
                "emotions": review.emotions,
                "keywords": review.keywords
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))