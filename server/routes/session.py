from fastapi import APIRouter, Header
from server.utils.chat_storage import delete_session_history

router = APIRouter(prefix="/session", tags=["Session"])


@router.delete("/logout")
def logout_cleanup(
    x_session_id: str = Header(...)
):
    """
    Delete all chat history associated with a session during logout.

    This endpoint performs cleanup of stored conversation data when a
    user logs out. It removes all messages, conversations, and related
    history tied to the provided session ID.

    The session is identified using the `x-session-id` request header.
    This ensures that only the data belonging to the active session
    is deleted.

    Args:
        x_session_id (str):
            Unique session identifier passed via request header.
            Required to locate and delete the correct session history.

    Returns:
        dict:
            Confirmation response indicating successful deletion.

            Example:
                {
                    "message": "Session history deleted."
                }

    Raises:
        HTTPException:
            - If the session ID is missing or invalid
            - If no history exists for the session
            - If deletion fails due to storage or server errors

    Notes:
        - This action is irreversible.
        - Typically called during user logout.
        - Does not invalidate authentication tokens unless handled
          separately by the auth system.

    Example:
        Request:
            DELETE /session/logout
            Header: x-session-id: abc123

        Response:
            {
                "message": "Session history deleted."
            }
    """
    delete_session_history(x_session_id)
    try:
        return {
            "message": "Session history deleted."
        }
    except Exception as e:
        return (f"The problem is this: {e}")
