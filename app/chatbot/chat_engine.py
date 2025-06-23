import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.chatbot.language_handler import language_handler
from app.chatbot.intent_classifier import intent_classifier
from app.core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


class ChatEngine:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        self.conversation_templates = {
            'greeting': {
                'en': "Hello! I'm your tourism assistant. How can I help you plan your visit today?",
                'es': "¡Hola! Soy tu asistente de turisme. ¿Cómo puedo ayudarte a planificar tu visita hoy?",
                'fr': "Bonjour! Je suis votre assistant touristique. Comment puis-je vous aider à planifier votre visite aujourd'hui?",
                'de': "Hallo! Ich bin Ihr Tourismusassistent. Wie kann ich Ihnen heute bei der Planung Ihres Besuchs helfen?",
            },
            'booking': {
                'en': "I'd be happy to help you with your booking. Could you please provide more details about what you'd like to book and for which dates?",
                'es': "Me complace ayudarte con tu reserva. ¿Podrías proporcionar más detalles sobre lo que te gustaría reservar y para qué fechas?",
                'fr': "Je serais ravi de vous aider avec votre réservation. Pourriez-vous fournir plus de détails sur ce que vous aimeriez réserver et pour quelles dates?",
                'de': "Gerne helfe ich Ihnen bei Ihrer Buchung. Könnten Sie bitte weitere Details darüber angeben, was Sie buchen möchten und für welche Termine?",
            },
            'unknown': {
                'en': "I understand you need help, but I'm not sure exactly what you're looking for. Could you please provide more specific information?",
                'es': "Entiendo que necesitas ayuda, pero no estoy seguro de qué buscas exactamente. ¿Podrías proporcionar información más específica?",
                'fr': "Je comprends que vous avez besoin d'aide, mais je ne suis pas sûr de ce que vous cherchez exactement. Pourriez-vous fournir des informations plus spécifiques?",
                'de': "Ich verstehe, dass Sie Hilfe benötigen, aber ich bin mir nicht sicher, wonach Sie genau suchen. Könnten Sie bitte spezifischere Informationen angeben?",
            }
        }
        
        self.business_context = {
            'general_info': """
            We are a tourism business that offers various services including:
            - Hotel accommodations
            - Tour packages
            - Local experiences
            - Transportation services
            - Restaurant recommendations
            
            Our operating hours are 9 AM to 6 PM, Monday to Sunday.
            We accept major credit cards and cash.
            """,
            'policies': """
            - Cancellation policy: Free cancellation up to 24 hours before the service
            - Check-in time: 3:00 PM
            - Check-out time: 11:00 AM
            - Pets are welcome with advance notice
            - Smoking is not allowed in indoor areas
            """
        }
    
    async def process_message(
        self, 
        session_id: str,
        user_message: str,
        business_id: str,
        user_language: Optional[str] = None
    ) -> Dict:
        """
        Process incoming user message and generate response
        """
        start_time = datetime.now()
        
        try:
            # Detect language if not provided
            if not user_language:
                user_language = await language_handler.detect_language(user_message)
            
            # Classify intent
            intent_result = await intent_classifier.classify_intent(user_message)
            
            # Extract entities
            entities = intent_classifier.extract_entities(user_message, intent_result['intent'])
            
            # Get conversation history
            conversation_history = await self._get_conversation_history(session_id)
            
            # Generate response
            response = await self._generate_response(
                user_message=user_message,
                intent=intent_result['intent'],
                entities=entities,
                conversation_history=conversation_history,
                user_language=user_language,
                business_id=business_id
            )
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Store conversation
            await self._store_conversation(
                session_id=session_id,
                user_message=user_message,
                assistant_response=response['content'],
                intent=intent_result['intent'],
                entities=entities,
                confidence=intent_result['confidence'],
                language=user_language,
                response_time=int(response_time)
            )
            
            return {
                'status': 'success',
                'response': response['content'],
                'intent': intent_result['intent'],
                'confidence': intent_result['confidence'],
                'entities': entities,
                'language': user_language,
                'response_time_ms': int(response_time),
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            error_response = await self._get_error_response(user_language or 'en')
            return {
                'status': 'error',
                'response': error_response,
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {},
                'language': user_language or 'en',
                'response_time_ms': int((datetime.now() - start_time).total_seconds() * 1000),
                'session_id': session_id,
                'error': str(e)
            }
    
    async def _generate_response(
        self,
        user_message: str,
        intent: str,
        entities: Dict,
        conversation_history: List[Dict],
        user_language: str,
        business_id: str
    ) -> Dict:
        """
        Generate appropriate response based on intent and context
        """
        try:
            # Use template responses for simple intents
            if intent in ['greeting', 'goodbye'] and intent in self.conversation_templates:
                template_responses = self.conversation_templates[intent]
                response = template_responses.get(user_language, template_responses['en'])
                return {'content': response, 'source': 'template'}
            
            # Use AI for complex responses
            if self.openai_client and intent not in ['greeting', 'goodbye']:
                ai_response = await self._generate_ai_response(
                    user_message, intent, entities, conversation_history, user_language, business_id
                )
                if ai_response:
                    return {'content': ai_response, 'source': 'ai'}
            
            # Fallback to template or rule-based responses
            return await self._generate_fallback_response(intent, entities, user_language)
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return await self._generate_fallback_response('unknown', {}, user_language)
    
    async def _generate_ai_response(
        self,
        user_message: str,
        intent: str,
        entities: Dict,
        conversation_history: List[Dict],
        user_language: str,
        business_id: str
    ) -> Optional[str]:
        """
        Generate AI-powered response using OpenAI
        """
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": f"""
                    You are a helpful tourism assistant for a tourism business. 
                    
                    Business Information:
                    {self.business_context['general_info']}
                    
                    Policies:
                    {self.business_context['policies']}
                    
                    User's detected intent: {intent}
                    Extracted entities: {json.dumps(entities)}
                    User's language: {user_language}
                    
                    Instructions:
                    1. Always respond in {user_language} if it's not English
                    2. Be helpful, friendly, and professional
                    3. Provide specific information when possible
                    4. If you don't know something, suggest how they can get more information
                    5. Keep responses concise but informative
                    6. If the user wants to book something, ask for specific details
                    7. Always prioritize customer satisfaction
                    """
                }
            ]
            
            # Add conversation history (last 5 messages)
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return None
    
    async def _generate_fallback_response(self, intent: str, entities: Dict, language: str) -> Dict:
        """
        Generate fallback response using templates and rules
        """
        responses = {
            'booking': {
                'en': "I'd be happy to help you with booking. Please provide more details about what you'd like to book, dates, and number of guests.",
                'es': "Me complace ayudarte con la reserva. Por favor proporciona más detalles sobre lo que quieres reservar, fechas y número de huéspedes.",
            },
            'information': {
                'en': "I can provide information about our services, hours, location, and policies. What specific information do you need?",
                'es': "Puedo proporcionar información sobre nuestros servicios, horarios, ubicación y políticas. ¿Qué información específica necesitas?",
            },
            'pricing': {
                'en': "Our pricing varies depending on the service and dates. Could you please specify what you're interested in?",
                'es': "Nuestros precios varían según el servicio y las fechas. ¿Podrías especificar en qué estás interesado?",
            },
            'complaint': {
                'en': "I'm sorry to hear about your concern. I'd like to help resolve this issue. Could you please provide more details?",
                'es': "Lamento escuchar sobre tu preocupación. Me gustaría ayudar a resolver este problema. ¿Podrías proporcionar más detalles?",
            },
            'unknown': self.conversation_templates['unknown']
        }
        
        intent_responses = responses.get(intent, responses['unknown'])
        response = intent_responses.get(language, intent_responses.get('en', 'I apologize, but I need more information to assist you properly.'))
        
        return {'content': response, 'source': 'fallback'}
    
    async def _get_error_response(self, language: str) -> str:
        """
        Get error response in appropriate language
        """
        error_responses = {
            'en': "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment.",
            'es': "Me disculpo, pero estoy experimentando algunas dificultades técnicas. Por favor intenta de nuevo en un momento.",
            'fr': "Je m'excuse, mais je rencontre des difficultés techniques. Veuillez réessayer dans un moment.",
            'de': "Entschuldigung, aber ich habe einige technische Schwierigkeiten. Bitte versuchen Sie es in einem Moment erneut.",
        }
        
        return error_responses.get(language, error_responses['en'])
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history from cache
        """
        try:
            cache_key = f"conversation:{session_id}"
            history = await redis_client.get_json(cache_key)
            return history or []
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def _store_conversation(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        intent: str,
        entities: Dict,
        confidence: float,
        language: str,
        response_time: int
    ):
        """
        Store conversation in cache and prepare for database storage
        """
        try:
            # Get existing history
            history = await self._get_conversation_history(session_id)
            
            # Add new messages
            history.extend([
                {
                    'role': 'user',
                    'content': user_message,
                    'timestamp': datetime.now().isoformat(),
                    'intent': intent,
                    'entities': entities,
                    'confidence': confidence,
                    'language': language
                },
                {
                    'role': 'assistant',
                    'content': assistant_response,
                    'timestamp': datetime.now().isoformat(),
                    'response_time_ms': response_time
                }
            ])
            
            # Keep only last 20 messages to manage memory
            if len(history) > 20:
                history = history[-20:]
            
            # Store in cache
            cache_key = f"conversation:{session_id}"
            await redis_client.set_json(cache_key, history, expire=3600)
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    async def create_session(self, business_id: str, user_language: str = 'en') -> str:
        """
        Create a new chat session
        """
        session_id = str(uuid.uuid4())
        
        # Initialize session in cache
        session_data = {
            'session_id': session_id,
            'business_id': business_id,
            'language': user_language,
            'created_at': datetime.now().isoformat(),
            'message_count': 0
        }
        
        cache_key = f"session:{session_id}"
        await redis_client.set_json(cache_key, session_data, expire=7200)  # 2 hours
        
        return session_id
    
    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session information
        """
        try:
            cache_key = f"session:{session_id}"
            return await redis_client.get_json(cache_key)
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None
    
    async def end_session(self, session_id: str):
        """
        End a chat session
        """
        try:
            # Clean up cache
            await redis_client.delete(f"session:{session_id}")
            await redis_client.delete(f"conversation:{session_id}")
        except Exception as e:
            logger.error(f"Error ending session: {e}")


# Global instance
chat_engine = ChatEngine()