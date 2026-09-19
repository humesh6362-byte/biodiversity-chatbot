from fastapi import APIRouter

from app.models import ChatRequest, ChatResponse
from app.chat.engine import handle_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    return handle_message(req)
