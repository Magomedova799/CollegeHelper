from fastapi import APIRouter, HTTPException
from pathlib import Path
from fastapi.responses import HTMLResponse
from app.assistant.schemas import AssistantRequest, AssistantResponse
from app.assistant.classifier import classify_message


router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)

@router.get("/", response_class=HTMLResponse)
def assistant_page():
    html_path = (
    Path(__file__).resolve().parent.parent.parent
    / "templates"
    / "assistant.html"
)
    return HTMLResponse(
        content=html_path.read_text(encoding="utf-8")
    )

@router.post("/chat", response_model=AssistantResponse)
async def chat_with_assistant(data: AssistantRequest):

    if not data.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Сообщение не может быть пустым"
        )

    try:
        result = await classify_message(data.message)

        return AssistantResponse(**result)

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"ИИ-помощник временно недоступен: {error}"
        )