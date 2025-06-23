import asyncio
import json
from typing import Dict, List, Optional, Tuple
import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
from app.core.config import settings
from app.core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self):
        self.emotion_pipeline = None
        self.sentiment_pipeline = None
        self.vader_analyzer = None
        self._initialize_models()
        
    def _initialize_models(self):
        try:
            # Download NLTK data if not present
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Initialize VADER sentiment analyzer (lightweight, no download required)
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            # Try to initialize Transformers models (optional, fallback if fails)
            try:
                from transformers import pipeline
                
                # Initialize emotion detection pipeline
                self.emotion_pipeline = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    return_all_scores=True
                )
                
                # Initialize sentiment pipeline
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                
                logger.info("Advanced sentiment models loaded successfully")
                
            except Exception as e:
                logger.warning(f"Advanced models not available, using fallback: {e}")
                self.emotion_pipeline = None
                self.sentiment_pipeline = None
            
        except Exception as e:
            logger.error(f"Error initializing sentiment models: {e}")
            self.emotion_pipeline = None
            self.sentiment_pipeline = None
            self.vader_analyzer = None
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict:
        """
        Analyze sentiment of given text
        """
        try:
            # Check cache first
            cache_key = f"sentiment:{hash(text)}"
            cached_result = await redis_client.get_json(cache_key)
            if cached_result:
                return cached_result
            
            result = {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0,
                "emotions": {},
                "keywords": []
            }
            
            if not text.strip():
                return result
            
            # Use VADER sentiment analyzer first (most reliable)
            if self.vader_analyzer:
                vader_scores = self.vader_analyzer.polarity_scores(text)
                result["sentiment_score"] = vader_scores['compound']
                result["confidence"] = abs(vader_scores['compound'])
                
                if vader_scores['compound'] >= 0.05:
                    result["sentiment_label"] = "positive"
                elif vader_scores['compound'] <= -0.05:
                    result["sentiment_label"] = "negative"
                else:
                    result["sentiment_label"] = "neutral"
            else:
                # Fallback to TextBlob
                blob = TextBlob(text)
                textblob_sentiment = blob.sentiment
                
                result["sentiment_score"] = textblob_sentiment.polarity
                result["confidence"] = abs(textblob_sentiment.polarity)
                
                if textblob_sentiment.polarity > 0.1:
                    result["sentiment_label"] = "positive"
                elif textblob_sentiment.polarity < -0.1:
                    result["sentiment_label"] = "negative"
                else:
                    result["sentiment_label"] = "neutral"
            
            # Advanced analysis if models are available
            if self.sentiment_pipeline:
                try:
                    sentiment_results = self.sentiment_pipeline(text)
                    if sentiment_results:
                        best_sentiment = max(sentiment_results[0], key=lambda x: x['score'])
                        
                        # Map Transformers labels to our format
                        label_mapping = {
                            'LABEL_0': 'negative',
                            'LABEL_1': 'neutral', 
                            'LABEL_2': 'positive',
                            'negative': 'negative',
                            'neutral': 'neutral',
                            'positive': 'positive'
                        }
                        
                        mapped_label = label_mapping.get(best_sentiment['label'].lower(), best_sentiment['label'].lower())
                        result["sentiment_label"] = mapped_label
                        result["confidence"] = max(result["confidence"], best_sentiment['score'])
                        
                        # Use Transformers score if confidence is higher
                        if best_sentiment['score'] > result["confidence"]:
                            if mapped_label == 'positive':
                                result["sentiment_score"] = best_sentiment['score']
                            elif mapped_label == 'negative':
                                result["sentiment_score"] = -best_sentiment['score']
                            else:
                                result["sentiment_score"] = 0.0
                            
                except Exception as e:
                    logger.warning(f"Advanced sentiment analysis failed: {e}")
            
            # Emotion analysis
            if self.emotion_pipeline:
                try:
                    emotion_results = self.emotion_pipeline(text)
                    if emotion_results:
                        emotions = {}
                        for emotion in emotion_results[0]:
                            emotions[emotion['label']] = emotion['score']
                        result["emotions"] = emotions
                except Exception as e:
                    logger.warning(f"Emotion analysis failed: {e}")
            
            # Extract keywords
            result["keywords"] = self._extract_keywords(text)
            
            # Cache the result
            await redis_client.set_json(cache_key, result, expire=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0,
                "emotions": {},
                "keywords": []
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text
        """
        try:
            blob = TextBlob(text)
            
            # Get noun phrases
            noun_phrases = list(blob.noun_phrases)
            
            # Get significant words (longer than 3 characters, not common words)
            words = blob.words
            significant_words = [
                word.lower() for word in words 
                if len(word) > 3 and word.lower() not in [
                    'this', 'that', 'with', 'have', 'will', 'from', 'they', 
                    'been', 'were', 'said', 'each', 'which', 'their', 'time',
                    'very', 'good', 'great', 'nice', 'love', 'like', 'really'
                ]
            ]
            
            # Combine and deduplicate
            all_keywords = list(set(noun_phrases + significant_words))
            
            # Return top 10 keywords
            return all_keywords[:10]
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
    
    async def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for multiple texts
        """
        tasks = [self.analyze_sentiment(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    async def get_sentiment_insights(self, reviews: List[Dict]) -> Dict:
        """
        Get overall sentiment insights from a collection of reviews
        """
        if not reviews:
            return {
                "overall_sentiment": "neutral",
                "average_score": 0.0,
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "top_emotions": {},
                "common_keywords": [],
                "total_reviews": 0
            }
        
        sentiments = []
        emotions_aggregate = {}
        all_keywords = []
        
        for review in reviews:
            if 'sentiment_score' in review:
                sentiments.append(review['sentiment_score'])
            
            if 'emotions' in review and review['emotions']:
                emotions = json.loads(review['emotions']) if isinstance(review['emotions'], str) else review['emotions']
                for emotion, score in emotions.items():
                    if emotion not in emotions_aggregate:
                        emotions_aggregate[emotion] = []
                    emotions_aggregate[emotion].append(score)
            
            if 'keywords' in review and review['keywords']:
                keywords = json.loads(review['keywords']) if isinstance(review['keywords'], str) else review['keywords']
                all_keywords.extend(keywords)
        
        avg_score = np.mean(sentiments) if sentiments else 0.0
        
        # Determine overall sentiment
        if avg_score > 0.1:
            overall_sentiment = "positive"
        elif avg_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Calculate sentiment distribution
        positive_count = sum(1 for s in sentiments if s > 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        # Top emotions
        top_emotions = {}
        for emotion, scores in emotions_aggregate.items():
            top_emotions[emotion] = np.mean(scores)
        
        # Sort emotions by average score
        top_emotions = dict(sorted(top_emotions.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Common keywords
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        common_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        common_keywords = [keyword for keyword, count in common_keywords]
        
        return {
            "overall_sentiment": overall_sentiment,
            "average_score": round(avg_score, 3),
            "sentiment_distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "top_emotions": top_emotions,
            "common_keywords": common_keywords,
            "total_reviews": len(reviews)
        }


# Global instance
sentiment_analyzer = SentimentAnalyzer()