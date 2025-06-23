from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from datetime import datetime, timedelta
import json

from app.models.chat import ChatSession, ChatMessage, ChatFeedback
from app.chatbot.chat_engine import chat_engine


class ChatService:
    
    @staticmethod
    async def create_chat_session(
        db: AsyncSession,
        business_id: str,
        user_id: Optional[str] = None,
        language: str = 'en',
        user_location: Optional[str] = None
    ) -> ChatSession:
        """
        Create a new chat session
        """
        # Create session ID using chat engine
        session_id = await chat_engine.create_session(business_id, language)
        
        # Create database record
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            business_id=business_id,
            language=language,
            user_location=user_location
        )
        
        db.add(chat_session)
        await db.commit()
        await db.refresh(chat_session)
        
        return chat_session
    
    @staticmethod
    async def send_message(
        db: AsyncSession,
        session_id: str,
        user_message: str,
        business_id: str
    ) -> Dict:
        """
        Send a message and get AI response
        """
        try:
            # Get session info
            session_query = select(ChatSession).where(ChatSession.session_id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                return {
                    'status': 'error',
                    'message': 'Session not found'
                }
            
            # Process message through chat engine
            chat_response = await chat_engine.process_message(
                session_id=session_id,
                user_message=user_message,
                business_id=business_id,
                user_language=session.language
            )
            
            if chat_response['status'] != 'success':
                return chat_response
            
            # Store user message
            user_msg = ChatMessage(
                session_id=session_id,
                message_type='user',
                content=user_message,
                original_language=chat_response['language'],
                intent=chat_response['intent'],
                confidence_score=chat_response['confidence'],
                entities=json.dumps(chat_response['entities'])
            )
            db.add(user_msg)
            
            # Store assistant response
            assistant_msg = ChatMessage(
                session_id=session_id,
                message_type='assistant',
                content=chat_response['response'],
                original_language=chat_response['language'],
                response_time_ms=chat_response['response_time_ms']
            )
            db.add(assistant_msg)
            
            await db.commit()
            
            return {
                'status': 'success',
                'response': chat_response['response'],
                'intent': chat_response['intent'],
                'confidence': chat_response['confidence'],
                'entities': chat_response['entities'],
                'language': chat_response['language'],
                'response_time_ms': chat_response['response_time_ms']
            }
            
        except Exception as e:
            await db.rollback()
            return {
                'status': 'error',
                'message': f'Message processing failed: {str(e)}'
            }
    
    @staticmethod
    async def get_chat_history(
        db: AsyncSession,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Get chat history for a session
        """
        query = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def end_chat_session(db: AsyncSession, session_id: str) -> bool:
        """
        End a chat session
        """
        try:
            # Update session status
            session_query = select(ChatSession).where(ChatSession.session_id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if session:
                session.is_active = False
                await db.commit()
                
                # Clean up chat engine session
                await chat_engine.end_session(session_id)
                
                return True
            
            return False
            
        except Exception as e:
            await db.rollback()
            return False
    
    @staticmethod
    async def add_feedback(
        db: AsyncSession,
        session_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        message_id: Optional[int] = None,
        issue_type: Optional[str] = None
    ) -> ChatFeedback:
        """
        Add feedback for a chat session or specific message
        """
        feedback = ChatFeedback(
            session_id=session_id,
            message_id=message_id,
            rating=rating,
            feedback_text=feedback_text,
            issue_type=issue_type
        )
        
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        
        return feedback
    
    @staticmethod
    async def get_chat_analytics(
        db: AsyncSession,
        business_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get chat analytics for a business
        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Base query for sessions in date range
            session_query = select(ChatSession).where(
                and_(
                    ChatSession.business_id == business_id,
                    ChatSession.created_at >= start_date,
                    ChatSession.created_at <= end_date
                )
            )
            
            # Total sessions
            total_sessions_result = await db.execute(
                select(func.count(ChatSession.id)).select_from(session_query.subquery())
            )
            total_sessions = total_sessions_result.scalar()
            
            # Active sessions
            active_sessions_result = await db.execute(
                select(func.count(ChatSession.id)).where(
                    and_(
                        ChatSession.business_id == business_id,
                        ChatSession.is_active == True
                    )
                )
            )
            active_sessions = active_sessions_result.scalar()
            
            # Messages analytics
            message_query = select(ChatMessage).join(ChatSession).where(
                and_(
                    ChatSession.business_id == business_id,
                    ChatMessage.created_at >= start_date,
                    ChatMessage.created_at <= end_date
                )
            )
            
            message_result = await db.execute(message_query)
            messages = message_result.scalars().all()
            
            # Process messages for analytics
            total_messages = len(messages)
            user_messages = [m for m in messages if m.message_type == 'user']
            assistant_messages = [m for m in messages if m.message_type == 'assistant']
            
            # Intent distribution
            intent_counts = {}
            confidence_scores = []
            
            for msg in user_messages:
                if msg.intent:
                    intent_counts[msg.intent] = intent_counts.get(msg.intent, 0) + 1
                if msg.confidence_score:
                    confidence_scores.append(msg.confidence_score)
            
            # Language distribution
            language_counts = {}
            for msg in user_messages:
                if msg.original_language:
                    lang = msg.original_language
                    language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Response time analytics
            response_times = [m.response_time_ms for m in assistant_messages if m.response_time_ms]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Feedback analytics
            feedback_query = select(ChatFeedback).join(ChatSession).where(
                and_(
                    ChatSession.business_id == business_id,
                    ChatFeedback.created_at >= start_date,
                    ChatFeedback.created_at <= end_date
                )
            )
            
            feedback_result = await db.execute(feedback_query)
            feedbacks = feedback_result.scalars().all()
            
            avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0
            
            return {
                'status': 'success',
                'analytics': {
                    'total_sessions': total_sessions,
                    'active_sessions': active_sessions,
                    'total_messages': total_messages,
                    'user_messages': len(user_messages),
                    'assistant_messages': len(assistant_messages),
                    'intent_distribution': intent_counts,
                    'language_distribution': language_counts,
                    'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                    'average_response_time_ms': avg_response_time,
                    'total_feedback': len(feedbacks),
                    'average_rating': round(avg_rating, 2),
                    'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()}
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Analytics calculation failed: {str(e)}'
            }
    
    @staticmethod
    async def get_popular_intents(
        db: AsyncSession,
        business_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get most popular intents for a business
        """
        try:
            # Get messages with intents from the last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            query = select(ChatMessage).join(ChatSession).where(
                and_(
                    ChatSession.business_id == business_id,
                    ChatMessage.message_type == 'user',
                    ChatMessage.intent.isnot(None),
                    ChatMessage.created_at >= cutoff_date
                )
            )
            
            result = await db.execute(query)
            messages = result.scalars().all()
            
            # Count intents
            intent_counts = {}
            for msg in messages:
                intent = msg.intent
                if intent not in intent_counts:
                    intent_counts[intent] = {'count': 0, 'avg_confidence': 0, 'confidence_scores': []}
                
                intent_counts[intent]['count'] += 1
                if msg.confidence_score:
                    intent_counts[intent]['confidence_scores'].append(msg.confidence_score)
            
            # Calculate averages and sort
            popular_intents = []
            for intent, data in intent_counts.items():
                avg_confidence = sum(data['confidence_scores']) / len(data['confidence_scores']) if data['confidence_scores'] else 0
                popular_intents.append({
                    'intent': intent,
                    'count': data['count'],
                    'average_confidence': round(avg_confidence, 3),
                    'percentage': round((data['count'] / len(messages)) * 100, 1) if messages else 0
                })
            
            # Sort by count and limit
            popular_intents.sort(key=lambda x: x['count'], reverse=True)
            return popular_intents[:limit]
            
        except Exception as e:
            return []
    
    @staticmethod
    async def get_session_summary(db: AsyncSession, session_id: str) -> Dict:
        """
        Get summary of a chat session
        """
        try:
            # Get session
            session_query = select(ChatSession).where(ChatSession.session_id == session_id)
            session_result = await db.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                return {'status': 'error', 'message': 'Session not found'}
            
            # Get messages
            messages_query = select(ChatMessage).where(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc())
            
            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()
            
            user_messages = [m for m in messages if m.message_type == 'user']
            assistant_messages = [m for m in messages if m.message_type == 'assistant']
            
            # Calculate metrics
            total_messages = len(messages)
            duration = (session.updated_at - session.created_at).total_seconds() if session.updated_at else 0
            
            intents = [msg.intent for msg in user_messages if msg.intent]
            unique_intents = list(set(intents))
            
            return {
                'status': 'success',
                'summary': {
                    'session_id': session_id,
                    'business_id': session.business_id,
                    'language': session.language,
                    'duration_seconds': duration,
                    'total_messages': total_messages,
                    'user_messages': len(user_messages),
                    'assistant_messages': len(assistant_messages),
                    'unique_intents': unique_intents,
                    'is_active': session.is_active,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.updated_at.isoformat() if session.updated_at else None
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Summary generation failed: {str(e)}'
            }