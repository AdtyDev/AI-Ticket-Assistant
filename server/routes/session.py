from fastapi import APIRouter, Header
from server.utils.chat_storage import delete_session_history

router = APIRouter(prefix="/session", tags=["Session"])


@router.delete("/logout")
def logout_cleanup(
    x_session_id: str = Header(...)
):
    delete_session_history(x_session_id)

    return {
        "message": "Session history deleted."
    }
