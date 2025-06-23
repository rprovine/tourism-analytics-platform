import re
from typing import Dict, List, Optional, Tuple
import json
from app.core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    def __init__(self):
        self.intents = {
            'booking': {
                'keywords': ['book', 'reserve', 'reservation', 'availability', 'available', 'schedule'],
                'patterns': [
                    r'\b(book|reserve|make.*reservation)\b',
                    r'\b(available|availability)\b',
                    r'\b(check.*in|check.*out)\b'
                ],
                'confidence_threshold': 0.6
            },
            'information': {
                'keywords': ['information', 'info', 'tell', 'what', 'where', 'when', 'how', 'hours', 'time', 'location'],
                'patterns': [
                    r'\b(what|where|when|how|why)\b',
                    r'\b(information|info|tell.*me|explain)\b',
                    r'\b(hours|opening|closing|time)\b',
                    r'\b(location|address|directions)\b'
                ],
                'confidence_threshold': 0.5
            },
            'pricing': {
                'keywords': ['price', 'cost', 'fee', 'charge', 'expensive', 'cheap', 'discount', 'rate'],
                'patterns': [
                    r'\b(price|cost|fee|charge|rate)\b',
                    r'\b(expensive|cheap|affordable)\b',
                    r'\b(discount|offer|deal|promotion)\b',
                    r'\$\d+|\d+.*dollar'
                ],
                'confidence_threshold': 0.7
            },
            'complaint': {
                'keywords': ['complaint', 'problem', 'issue', 'wrong', 'bad', 'terrible', 'disappointed', 'unsatisfied'],
                'patterns': [
                    r'\b(complaint|complain|problem|issue)\b',
                    r'\b(wrong|bad|terrible|awful|horrible)\b',
                    r'\b(disappointed|unsatisfied|unhappy)\b'
                ],
                'confidence_threshold': 0.8
            },
            'cancellation': {
                'keywords': ['cancel', 'cancellation', 'refund', 'change', 'modify'],
                'patterns': [
                    r'\b(cancel|cancellation)\b',
                    r'\b(refund|money.*back)\b',
                    r'\b(change|modify|reschedule)\b'
                ],
                'confidence_threshold': 0.8
            },
            'recommendation': {
                'keywords': ['recommend', 'suggest', 'best', 'good', 'popular', 'famous', 'must', 'should'],
                'patterns': [
                    r'\b(recommend|suggest|advice)\b',
                    r'\b(best|good|great|popular|famous)\b',
                    r'\b(must.*see|should.*visit|worth.*visiting)\b'
                ],
                'confidence_threshold': 0.6
            },
            'directions': {
                'keywords': ['direction', 'how to get', 'way', 'route', 'transport', 'bus', 'train', 'taxi'],
                'patterns': [
                    r'\b(direction|how.*get|way.*to)\b',
                    r'\b(route|path|navigate)\b',
                    r'\b(transport|bus|train|taxi|uber|metro)\b'
                ],
                'confidence_threshold': 0.7
            },
            'weather': {
                'keywords': ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'forecast'],
                'patterns': [
                    r'\b(weather|temperature|climate)\b',
                    r'\b(rain|sunny|cloudy|snow|storm)\b',
                    r'\b(forecast|today.*weather|tomorrow.*weather)\b'
                ],
                'confidence_threshold': 0.8
            },
            'greeting': {
                'keywords': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                'patterns': [
                    r'\b(hello|hi|hey|greetings)\b',
                    r'\b(good\s*(morning|afternoon|evening|day))\b'
                ],
                'confidence_threshold': 0.9
            },
            'goodbye': {
                'keywords': ['bye', 'goodbye', 'see you', 'farewell', 'thanks', 'thank you'],
                'patterns': [
                    r'\b(bye|goodbye|farewell)\b',
                    r'\b(see.*you|talk.*later)\b',
                    r'\b(thanks|thank.*you)\b'
                ],
                'confidence_threshold': 0.9
            }
        }
    
    async def classify_intent(self, text: str) -> Dict:
        """
        Classify the intent of the user message
        """
        try:
            # Check cache first
            cache_key = f"intent:{hash(text)}"
            cached_result = await redis_client.get_json(cache_key)
            if cached_result:
                return cached_result
            
            text_lower = text.lower()
            intent_scores = {}
            
            # Calculate scores for each intent
            for intent_name, intent_data in self.intents.items():
                score = 0
                matched_keywords = []
                matched_patterns = []
                
                # Check keywords
                for keyword in intent_data['keywords']:
                    if keyword.lower() in text_lower:
                        score += 1
                        matched_keywords.append(keyword)
                
                # Check patterns
                for pattern in intent_data['patterns']:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        score += 2  # Patterns have higher weight
                        matched_patterns.append(pattern)
                
                # Normalize score
                total_possible = len(intent_data['keywords']) + (len(intent_data['patterns']) * 2)
                normalized_score = score / total_possible if total_possible > 0 else 0
                
                intent_scores[intent_name] = {
                    'score': normalized_score,
                    'raw_score': score,
                    'matched_keywords': matched_keywords,
                    'matched_patterns': matched_patterns,
                    'threshold': intent_data['confidence_threshold']
                }
            
            # Find the best intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1]['score'])
            intent_name, intent_info = best_intent
            
            # Check if confidence meets threshold
            confidence = intent_info['score']
            if confidence >= intent_info['threshold']:
                result = {
                    'intent': intent_name,
                    'confidence': round(confidence, 3),
                    'matched_keywords': intent_info['matched_keywords'],
                    'matched_patterns': intent_info['matched_patterns'],
                    'all_scores': {k: v['score'] for k, v in intent_scores.items()}
                }
            else:
                result = {
                    'intent': 'unknown',
                    'confidence': 0.0,
                    'matched_keywords': [],
                    'matched_patterns': [],
                    'all_scores': {k: v['score'] for k, v in intent_scores.items()}
                }
            
            # Cache the result
            await redis_client.set_json(cache_key, result, expire=1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'matched_keywords': [],
                'matched_patterns': [],
                'all_scores': {}
            }
    
    def extract_entities(self, text: str, intent: str) -> Dict:
        """
        Extract entities from text based on intent
        """
        entities = {}
        text_lower = text.lower()
        
        try:
            # Date/time extraction
            date_patterns = [
                r'\b(today|tomorrow|yesterday)\b',
                r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
                r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    entities['dates'] = matches
                    break
            
            # Number extraction
            number_patterns = [
                r'\b(\d+)\s*(people|person|guest|adult|child)\b',
                r'\b(\d+)\s*(night|day|hour)\b',
                r'\$(\d+(?:\.\d{2})?)\b'
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    if 'numbers' not in entities:
                        entities['numbers'] = []
                    entities['numbers'].extend(matches)
            
            # Location extraction (simple approach)
            location_indicators = ['in', 'at', 'near', 'to', 'from']
            for indicator in location_indicators:
                pattern = rf'\b{indicator}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities['locations'] = matches
                    break
            
            # Intent-specific entity extraction
            if intent == 'booking':
                # Extract room types, service types
                room_types = ['single', 'double', 'suite', 'family', 'deluxe']
                for room_type in room_types:
                    if room_type in text_lower:
                        if 'room_types' not in entities:
                            entities['room_types'] = []
                        entities['room_types'].append(room_type)
            
            elif intent == 'pricing':
                # Extract service names
                service_patterns = [
                    r'\b(room|hotel|flight|tour|ticket|rental)\b'
                ]
                for pattern in service_patterns:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        entities['services'] = matches
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return {}
    
    async def get_intent_statistics(self) -> Dict:
        """
        Get statistics about intent classification
        """
        return {
            'total_intents': len(self.intents),
            'intent_names': list(self.intents.keys()),
            'intent_details': {
                name: {
                    'keywords_count': len(data['keywords']),
                    'patterns_count': len(data['patterns']),
                    'threshold': data['confidence_threshold']
                }
                for name, data in self.intents.items()
            }
        }


# Global instance
intent_classifier = IntentClassifier()