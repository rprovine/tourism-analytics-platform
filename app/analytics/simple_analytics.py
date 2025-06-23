"""
Simple analytics without heavy ML dependencies
Uses basic statistical methods instead of scikit-learn
"""
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

class SimpleAnalytics:
    """Analytics using basic Python math instead of ML libraries"""
    
    @staticmethod
    def analyze_sentiment_simple(text: str) -> Dict[str, Any]:
        """Simple sentiment analysis using word lists"""
        positive_words = [
            'amazing', 'excellent', 'fantastic', 'wonderful', 'great', 'perfect', 
            'beautiful', 'outstanding', 'brilliant', 'superb', 'incredible', 
            'lovely', 'awesome', 'fabulous', 'spectacular', 'marvelous',
            'good', 'nice', 'pleasant', 'enjoyable', 'comfortable', 'clean',
            'friendly', 'helpful', 'professional', 'luxury', 'luxurious'
        ]
        
        negative_words = [
            'terrible', 'awful', 'horrible', 'disgusting', 'dirty', 'broken',
            'bad', 'poor', 'disappointing', 'unacceptable', 'rude', 'unfriendly',
            'expensive', 'overpriced', 'noisy', 'uncomfortable', 'outdated',
            'cramped', 'smelly', 'cold', 'hot', 'slow', 'unprofessional'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.95, 0.6 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.95, 0.6 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
            
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_words": positive_count,
            "negative_words": negative_count
        }
    
    @staticmethod
    def simple_forecast(historical_data: List[Dict], days: int = 30) -> List[Dict]:
        """Simple forecasting using moving averages"""
        if not historical_data:
            return []
            
        # Calculate recent averages
        recent_data = historical_data[-14:]  # Last 2 weeks
        
        avg_occupancy = statistics.mean([d.get('occupancy_rate', 65) for d in recent_data])
        avg_revenue = statistics.mean([d.get('revenue', 15000) for d in recent_data])
        avg_bookings = statistics.mean([d.get('bookings', 50) for d in recent_data])
        
        # Simple trend calculation
        if len(recent_data) >= 7:
            early_avg = statistics.mean([d.get('occupancy_rate', 65) for d in recent_data[:7]])
            late_avg = statistics.mean([d.get('occupancy_rate', 65) for d in recent_data[7:]])
            trend = (late_avg - early_avg) / early_avg if early_avg > 0 else 0
        else:
            trend = 0.02  # Assume 2% growth
            
        forecast = []
        base_date = datetime.now()
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Apply trend and seasonal variations
            seasonal_factor = 1.0 + 0.1 * (i % 7 >= 5)  # Weekend boost
            trend_factor = 1.0 + (trend * i / 30)  # Apply trend over time
            
            # Add some randomness
            random_factor = 1.0 + random.uniform(-0.1, 0.1)
            
            forecasted_occupancy = avg_occupancy * seasonal_factor * trend_factor * random_factor
            forecasted_occupancy = max(30, min(95, forecasted_occupancy))  # Clamp values
            
            forecasted_revenue = avg_revenue * (forecasted_occupancy / avg_occupancy) * random_factor
            forecasted_bookings = int(avg_bookings * (forecasted_occupancy / avg_occupancy) * random_factor)
            
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "occupancy_rate": round(forecasted_occupancy, 1),
                "revenue": round(forecasted_revenue, 2),
                "bookings": forecasted_bookings,
                "confidence": max(0.6, 0.9 - (i * 0.01))  # Decreasing confidence over time
            })
            
        return forecast
    
    @staticmethod
    def calculate_hotel_metrics(hotel_data: List[Dict]) -> Dict[str, Any]:
        """Calculate basic hotel performance metrics"""
        if not hotel_data:
            return {}
            
        total_revenue = sum(d.get('revenue', 0) for d in hotel_data)
        avg_occupancy = statistics.mean([d.get('occupancy_rate', 0) for d in hotel_data])
        total_bookings = sum(d.get('bookings', 0) for d in hotel_data)
        
        # Revenue per available room (RevPAR) approximation
        avg_rooms = statistics.mean([d.get('rooms', 100) for d in hotel_data])
        revpar = total_revenue / (len(hotel_data) * avg_rooms) if hotel_data and avg_rooms > 0 else 0
        
        return {
            "total_revenue": round(total_revenue, 2),
            "average_occupancy": round(avg_occupancy, 1),
            "total_bookings": total_bookings,
            "revenue_per_available_room": round(revpar, 2),
            "performance_trend": "stable" if abs(avg_occupancy - 70) < 10 else ("strong" if avg_occupancy > 80 else "weak")
        }
    
    @staticmethod
    def analyze_reviews_batch(reviews: List[Dict]) -> Dict[str, Any]:
        """Analyze multiple reviews for patterns"""
        if not reviews:
            return {}
            
        sentiments = []
        ratings = []
        
        for review in reviews:
            if 'review_text' in review:
                sentiment_result = SimpleAnalytics.analyze_sentiment_simple(review['review_text'])
                sentiments.append(sentiment_result['sentiment'])
            
            if 'rating' in review:
                ratings.append(review['rating'])
        
        # Count sentiments
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'neutral': sentiments.count('neutral'),
            'negative': sentiments.count('negative')
        }
        
        avg_rating = statistics.mean(ratings) if ratings else 0
        
        return {
            "sentiment_distribution": sentiment_counts,
            "average_rating": round(avg_rating, 1),
            "total_reviews": len(reviews),
            "satisfaction_level": "high" if avg_rating >= 4.0 else ("medium" if avg_rating >= 3.0 else "low")
        }