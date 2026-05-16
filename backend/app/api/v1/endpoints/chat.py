from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from app.services.rag_service import rag_service
from app.api.v1.endpoints.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, Chat, Message
from app.services.feedback_service import feedback_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    chat_id: int = None
    provider: str = None

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    is_positive: bool

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. Get or Create Chat Session
        if request.chat_id:
            chat = db.query(Chat).filter(Chat.id == request.chat_id, Chat.user_id == current_user.id).first()
            if not chat:
                raise HTTPException(status_code=404, detail="Chat session not found")
        else:
            chat = Chat(user_id=current_user.id, title=request.message[:50])
            db.add(chat)
            db.commit()
            db.refresh(chat)

        # 2. Save User Message
        user_msg = Message(chat_id=chat.id, role="user", content=request.message)
        db.add(user_msg)
        db.commit()

        # 3. Get AI Response
        response = await rag_service.answer_query(request.message, provider=request.provider)

        # 4. Save Assistant Message
        assistant_msg = Message(
            chat_id=chat.id, 
            role="assistant", 
            content=response["answer"],
            sources=json.dumps(response.get("sources", [])),
            agent_logs=json.dumps(response.get("agent_logs", []))
        )
        db.add(assistant_msg)
        db.commit()

        # Return response with chat_id for frontend persistence
        response["chat_id"] = chat.id
        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest):
    try:
        if request.is_positive:
            # Store as "Gold Standard" in Pinecone for future retrieval
            feedback_service.save_positive_feedback(request.query, request.answer)
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
