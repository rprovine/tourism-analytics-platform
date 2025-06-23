from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.services.chat_service import ChatService

router = APIRouter()


class ChatSessionCreate(BaseModel):
    business_id: str
    user_id: Optional[str] = None
    language: str = "en"
    user_location: Optional[str] = None


class ChatMessage(BaseModel):
    session_id: str
    message: str
    business_id: str


class ChatFeedback(BaseModel):
    session_id: str
    rating: int
    feedback_text: Optional[str] = None
    message_id: Optional[int] = None
    issue_type: Optional[str] = None


@router.post("/session")
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session"""
    try:
        session = await ChatService.create_chat_session(
            db=db,
            business_id=session_data.business_id,
            user_id=session_data.user_id,
            language=session_data.language,
            user_location=session_data.user_location
        )
        
        return {
            "status": "success",
            "session_id": session.session_id,
            "message": "Chat session created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message")
async def send_message(
    message_data: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response"""
    try:
        response = await ChatService.send_message(
            db=db,
            session_id=message_data.session_id,
            user_message=message_data.message,
            business_id=message_data.business_id
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history")
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a session"""
    try:
        messages = await ChatService.get_chat_history(db, session_id, limit)
        
        return {
            "status": "success",
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "message_type": msg.message_type,
                    "content": msg.content,
                    "original_language": msg.original_language,
                    "translated_content": msg.translated_content,
                    "intent": msg.intent,
                    "confidence_score": msg.confidence_score,
                    "entities": msg.entities,
                    "response_time_ms": msg.response_time_ms,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def end_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """End a chat session"""
    try:
        success = await ChatService.end_chat_session(db, session_id)
        
        if success:
            return {
                "status": "success",
                "message": "Chat session ended successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def add_chat_feedback(
    feedback_data: ChatFeedback,
    db: AsyncSession = Depends(get_db)
):
    """Add feedback for a chat session"""
    try:
        feedback = await ChatService.add_feedback(
            db=db,
            session_id=feedback_data.session_id,
            rating=feedback_data.rating,
            feedback_text=feedback_data.feedback_text,
            message_id=feedback_data.message_id,
            issue_type=feedback_data.issue_type
        )
        
        return {
            "status": "success",
            "feedback_id": feedback.id,
            "message": "Feedback added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_chat_analytics(
    business_id: str = Query(..., description="Business ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    """Get chat analytics for a business"""
    try:
        analytics = await ChatService.get_chat_analytics(
            db, business_id, start_date, end_date
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intents/popular")
async def get_popular_intents(
    business_id: str = Query(..., description="Business ID"),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get most popular chat intents"""
    try:
        intents = await ChatService.get_popular_intents(db, business_id, limit)
        
        return {
            "status": "success",
            "popular_intents": intents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get summary of a chat session"""
    try:
        summary = await ChatService.get_session_summary(db, session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))