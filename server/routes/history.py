from fastapi import APIRouter, Header
from server.utils.chat_storage import (load_messages,list_conversations)

router = APIRouter(prefix="/history", tags=["History"])



# List conversations
@router.get("/")
def get_conversations(
    x_session_id: str = Header(...)
):
    """
    Retrieve all conversations associated with a session.

    This endpoint returns a list of conversation metadata
    (e.g., conversation IDs, titles, timestamps) that belong
    to the provided session.

    The session is identified using the `x-session-id` header,
    which acts as a unique identifier for a user or client.

    Args:
        x_session_id (str):
            Unique session identifier passed via request header.
            Required to fetch conversations for the correct user.

    Returns:
        list[dict]:
            A list of conversations. Each item typically contains:
                - conv_id: Unique conversation ID
                - title: Conversation title or summary
                - created_at: Creation timestamp
                - updated_at: Last activity timestamp

            (Exact structure depends on `list_conversations` implementation.)

    Raises:
        HTTPException:
            - If the session ID is missing or invalid
            - If storage retrieval fails

    Example:
        Request:
            GET /history/
            Header: x-session-id: abc123

        Response:
            [
                {
                    "conv_id": "conv_1",
                    "title": "Project discussion",
                    "created_at": "2026-02-10T12:00:00Z"
                }
            ]
    """
    try:
        return list_conversations(x_session_id)
    except Exception as e:
        return (f"The problem is this: {e}")


# Get messages
@router.get("/{conv_id}")
def get_messages(
    conv_id: str,
    x_session_id: str = Header(...)
):
    """
        Retrieve all messages for a specific conversation.

        This endpoint loads the full message history for a given
        conversation ID, scoped to the provided session.

        Both the conversation ID and session ID are required to
        ensure messages are fetched securely and belong to the
        correct user session.

        Args:
            conv_id (str):
                Unique identifier of the conversation whose messages
                should be retrieved.

            x_session_id (str):
                Session identifier passed via request header.
                Used to validate ownership of the conversation.

        Returns:
            list[dict]:
                A list of message objects in chronological order.
                Each message may contain:
                    - role: Sender role (e.g., "user", "assistant")
                    - content: Message text
                    - timestamp: Message creation time

                (Structure depends on `load_messages` implementation.)

        Raises:
            HTTPException:
                - If the conversation does not exist
                - If the session does not have access
                - If message storage fails

        Example:
            Request:
                GET /history/conv_1
                Header: x-session-id: abc123

            Response:
                [
                    {
                        "role": "user",
                        "content": "Hello",
                        "timestamp": "2026-02-10T12:01:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "Hi! How can I help?",
                        "timestamp": "2026-02-10T12:01:02Z"
                    }
                ]
        """
    try:
        return load_messages(x_session_id, conv_id)
    except Exception as e:
        return (f"The problem is this: {e}")
