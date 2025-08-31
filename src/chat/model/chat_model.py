from typing import List
from pydantic import BaseModel, Field


class ConversationRequestModel(BaseModel):
    context_id: str = Field(..., strict=True, description="context id")
    user_id: str = Field(..., strict=True, description="user id")
    user_prompt: str = Field(..., strict=True, description="user query")
