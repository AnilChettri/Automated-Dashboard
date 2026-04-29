"""
Chat Pydantic schemas for the NL→SQL chatbot.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="Natural language question")
    session_id: str | None = Field(default=None, description="Chat session ID for context")


class ChatResponse(BaseModel):
    answer: str
    sql_query: str | None = None
    data: list[dict] | None = None
    chart_suggestion: str | None = None  # bar, line, pie, table
    session_id: str
    is_successful: bool = True
    error: str | None = None


class ChatHistoryItem(BaseModel):
    id: int
    user_query: str
    ai_explanation: str | None
    generated_sql: str | None
    is_successful: bool
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryItem]
    session_id: str


class ChatRatingRequest(BaseModel):
    chat_id: int
    rating: int = Field(..., ge=1, le=5)


class RecommendationItem(BaseModel):
    title: str
    description: str
    priority: str  # high, medium, low
    category: str  # retention, growth, efficiency
    confidence: float | None = None
    action_items: list[str] = []


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationItem]
    generated_at: str
