"""
Chat API Routes
NL → SQL chatbot interface.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ai_service
from app.config import get_settings

router = APIRouter(prefix="/api/chat", tags=["Chat"])
settings = get_settings()

@router.get("/status")
async def chat_status():
    """Check if AI chat is available."""
    return {
        "available": ai_service.enabled,
        "model": ai_service.model,
        "message": "AI chat ready" if ai_service.enabled else "OpenAI API key not configured. Add OPENAI_API_KEY to .env",
    }

@router.post("/ask", response_model=ChatResponse)
async def ask_data(request: ChatRequest):
    """Ask a natural language question about the business data."""
    if not ai_service.enabled:
        raise HTTPException(status_code=503, detail="AI is not configured")
        
    session_id = request.session_id or str(uuid.uuid4())
    
    # Run the AI workflow
    result = await ai_service.ask_data(request.query, session_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return ChatResponse(
        answer=result["answer"],
        sql_query=result["sql_query"],
        data=result["data"],
        chart_suggestion=result["chart_suggestion"],
        session_id=result["session_id"],
        is_successful=True
    )

