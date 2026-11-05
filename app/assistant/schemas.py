from typing import Literal
from pydantic import BaseModel


class AssistantRequest(BaseModel):
    message: str


class AssistantDraft(BaseModel):
    title: str
    description: str


class AssistantResponse(BaseModel):
    type: Literal["information", "malfunction", "danger"]
    answer: str
    category: str | None = None
    confidence: float
    suggest_create_request: bool = False
    draft: AssistantDraft | None = None
    needs_clarification: bool = False
    human_review: bool = False