from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    is_positive: bool

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        return await rag_service.answer_query(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest):
    try:
        if request.is_positive:
            # Store as "Gold Standard" for future few-shot learning
            from app.services.feedback_service import feedback_service
            feedback_service.save_positive_feedback(request.query, request.answer)
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
