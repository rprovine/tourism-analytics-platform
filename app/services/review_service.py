from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import json
from datetime import datetime, timedelta

from app.models.review import Review
from app.analytics.sentiment_analyzer import sentiment_analyzer
from app.core.database import get_db


class ReviewService:
    
    @staticmethod
    async def create_review(db: AsyncSession, review_data: Dict) -> Review:
        """
        Create a new review
        """
        review = Review(**review_data)
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review
    
    @staticmethod
    async def process_review_sentiment(db: AsyncSession, review_id: int) -> Optional[Review]:
        """
        Process sentiment analysis for a review
        """
        # Get the review
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one_or_none()
        
        if not review or review.processed:
            return review
        
        # Analyze sentiment
        sentiment_result = await sentiment_analyzer.analyze_sentiment(
            review.review_text, 
            review.language
        )
        
        # Update review with sentiment data
        review.sentiment_score = sentiment_result['sentiment_score']
        review.sentiment_label = sentiment_result['sentiment_label']
        review.emotions = json.dumps(sentiment_result['emotions'])
        review.keywords = json.dumps(sentiment_result['keywords'])
        review.processed = True
        
        await db.commit()
        await db.refresh(review)
        
        return review
    
    @staticmethod
    async def get_reviews(
        db: AsyncSession,
        business_id: Optional[str] = None,
        sentiment_label: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Review]:
        """
        Get reviews with filters
        """
        query = select(Review)
        
        conditions = []
        
        if business_id:
            conditions.append(Review.business_id == business_id)
        
        if sentiment_label:
            conditions.append(Review.sentiment_label == sentiment_label)
        
        if min_rating is not None:
            conditions.append(Review.rating >= min_rating)
        
        if max_rating is not None:
            conditions.append(Review.rating <= max_rating)
        
        if start_date:
            conditions.append(Review.created_at >= start_date)
        
        if end_date:
            conditions.append(Review.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Review.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_sentiment_analytics(
        db: AsyncSession,
        business_id: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Get sentiment analytics for reviews
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Base query
        query = select(Review).where(
            and_(
                Review.created_at >= start_date,
                Review.processed == True
            )
        )
        
        if business_id:
            query = query.where(Review.business_id == business_id)
        
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        # Convert to dict format for analysis
        review_dicts = []
        for review in reviews:
            review_dict = {
                'sentiment_score': review.sentiment_score,
                'sentiment_label': review.sentiment_label,
                'emotions': review.emotions,
                'keywords': review.keywords,
                'rating': review.rating,
                'created_at': review.created_at
            }
            review_dicts.append(review_dict)
        
        # Get insights
        insights = await sentiment_analyzer.get_sentiment_insights(review_dicts)
        
        # Add time-based analysis
        insights['trend_analysis'] = await ReviewService._get_sentiment_trends(
            review_dicts, days
        )
        
        return insights
    
    @staticmethod
    async def _get_sentiment_trends(reviews: List[Dict], days: int) -> Dict:
        """
        Analyze sentiment trends over time
        """
        if not reviews:
            return {"daily_scores": [], "trend": "stable"}
        
        # Group reviews by date
        daily_scores = {}
        for review in reviews:
            if review['created_at'] and review['sentiment_score'] is not None:
                date_key = review['created_at'].date().isoformat()
                if date_key not in daily_scores:
                    daily_scores[date_key] = []
                daily_scores[date_key].append(review['sentiment_score'])
        
        # Calculate daily averages
        daily_averages = []
        for date_key in sorted(daily_scores.keys()):
            avg_score = sum(daily_scores[date_key]) / len(daily_scores[date_key])
            daily_averages.append({
                'date': date_key,
                'avg_sentiment': round(avg_score, 3),
                'review_count': len(daily_scores[date_key])
            })
        
        # Determine trend
        trend = "stable"
        if len(daily_averages) >= 2:
            recent_avg = sum([day['avg_sentiment'] for day in daily_averages[-7:]]) / min(7, len(daily_averages))
            older_avg = sum([day['avg_sentiment'] for day in daily_averages[:-7]]) / max(1, len(daily_averages) - 7)
            
            if recent_avg > older_avg + 0.1:
                trend = "improving"
            elif recent_avg < older_avg - 0.1:
                trend = "declining"
        
        return {
            "daily_scores": daily_averages,
            "trend": trend
        }
    
    @staticmethod
    async def bulk_process_unprocessed_reviews(db: AsyncSession, limit: int = 50) -> int:
        """
        Process sentiment for unprocessed reviews in bulk
        """
        # Get unprocessed reviews
        query = select(Review).where(Review.processed == False).limit(limit)
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        processed_count = 0
        for review in reviews:
            try:
                await ReviewService.process_review_sentiment(db, review.id)
                processed_count += 1
            except Exception as e:
                print(f"Error processing review {review.id}: {e}")
                continue
        
        return processed_count
    
    @staticmethod
    async def get_review_statistics(
        db: AsyncSession,
        business_id: Optional[str] = None
    ) -> Dict:
        """
        Get overall review statistics
        """
        query = select(Review)
        if business_id:
            query = query.where(Review.business_id == business_id)
        
        # Total count
        count_result = await db.execute(
            select(func.count(Review.id)).select_from(query.subquery())
        )
        total_reviews = count_result.scalar()
        
        # Average rating
        avg_result = await db.execute(
            select(func.avg(Review.rating)).select_from(query.subquery())
        )
        avg_rating = avg_result.scalar() or 0.0
        
        # Sentiment distribution
        sentiment_query = query.where(Review.processed == True)
        sentiment_result = await db.execute(sentiment_query)
        processed_reviews = sentiment_result.scalars().all()
        
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for review in processed_reviews:
            if review.sentiment_label in sentiment_counts:
                sentiment_counts[review.sentiment_label] += 1
        
        return {
            "total_reviews": total_reviews,
            "processed_reviews": len(processed_reviews),
            "average_rating": round(avg_rating, 2),
            "sentiment_distribution": sentiment_counts
        }