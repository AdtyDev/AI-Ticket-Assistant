from fastapi import APIRouter, Header
from server.utils.chat_storage import (load_messages,list_conversations)

router = APIRouter(prefix="/history", tags=["History"])



# List conversations
@router.get("/")
def get_conversations(
    x_session_id: str = Header(...)
):
    return list_conversations(x_session_id)


# Get messages
@router.get("/{conv_id}")
def get_messages(
    conv_id: str,
    x_session_id: str = Header(...)
):
    return load_messages(x_session_id, conv_id)
