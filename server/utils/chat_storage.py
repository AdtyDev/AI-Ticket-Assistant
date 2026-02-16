import json
import os

STORE_PATH = "server/chat_store"


# Internal helper
def _file_path(session_id, conv_id):
    """
    Construct the file path for a conversation's storage file.

    Each conversation is stored as a JSON file using the naming
    convention:

        {session_id}_{conv_id}.json

    Args:
        session_id (str):
            Unique identifier for the user session.

        conv_id (str):
            Unique identifier for the conversation.

    Returns:
        str:
            Absolute/relative file path where the conversation
            messages are stored.
    """
    return f"{STORE_PATH}/{session_id}_{conv_id}.json"



# Save message
def save_message(session_id, conv_id, role, content):
    """
    Save a message to a conversation history file.

    This function appends a new message to the JSON file associated
    with the given session and conversation. If the file does not
    exist, it is created automatically.

    Messages are stored in chronological order as a list of objects.

    Storage format example:
        [
            {
                "role": "user",
                "content": "Hello"
            },
            {
                "role": "assistant",
                "content": "Hi! How can I help?"
            }
        ]

    Args:
        session_id (str):
            Unique session identifier.

        conv_id (str):
            Conversation identifier.

        role (str):
            Sender role (e.g., "user", "assistant", "system").

        content (str):
            Message text content.

    Side Effects:
        - Creates storage directory if it does not exist
        - Creates conversation file if missing
        - Writes updated message list to disk

    Raises:
        json.JSONDecodeError:
            If an existing file contains invalid JSON.

        OSError:
            If file writing fails due to permission or disk issues.
    """

    os.makedirs(STORE_PATH, exist_ok=True)

    path = _file_path(session_id, conv_id)

    data = []

    # Load existing messages
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)

    # Append new message
    data.append({
        "role": role,
        "content": content
    })

    # Save back
    with open(path, "w") as f:
        json.dump(data, f, indent=2)



# Load messages
def load_messages(session_id, conv_id):
    """
    Load all messages for a given conversation.

    This function reads the conversation JSON file and returns
    the stored message history in chronological order.

    Args:
        session_id (str):
            Unique session identifier.

        conv_id (str):
            Conversation identifier.

    Returns:
        list[dict]:
            List of message objects containing:
                - role (str)
                - content (str)

            Returns an empty list if no conversation exists.

    Raises:
        json.JSONDecodeError:
            If the conversation file contains invalid JSON.

        OSError:
            If file reading fails.
    """
    path = _file_path(session_id, conv_id)

    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        return json.load(f)


# List conversations
def list_conversations(session_id):
    """
    List all conversation IDs for a session.

    This function scans the storage directory and extracts
    conversation identifiers belonging to the specified session.

    It relies on the file naming convention:

        {session_id}_{conv_id}.json

    Args:
        session_id (str):
            Unique session identifier whose conversations
            should be listed.

    Returns:
        list[str]:
            List of conversation IDs associated with the session.

            Example:
                ["conv_1", "conv_2", "support_chat"]

        Returns an empty list if no conversations exist
        or if the storage directory is missing.

    Notes:
        - Only filenames starting with the session ID are considered.
        - File extension `.json` is stripped from results.
    """
    if not os.path.exists(STORE_PATH):
        return []

    files = os.listdir(STORE_PATH)

    convs = []

    for f in files:
        if f.startswith(session_id):
            conv_id = (
                f.replace(f"{session_id}_", "")
                .replace(".json", "")
            )
            convs.append(conv_id)

    return convs


def delete_session_history(session_id):
    """
    Delete all conversation history for a session.

    This function removes every conversation file associated
    with the provided session ID from storage.

    It is typically used during logout or session cleanup.

    Args:
        session_id (str):
            Unique session identifier whose history
            should be deleted.

    Side Effects:
        - Permanently deletes conversation files from disk.

    Returns:
        None

    Raises:
        OSError:
            If file deletion fails due to permission issues.

    Warning:
        This action is irreversible. All conversation data
        for the session will be permanently lost.

    Example:
        > delete_session_history("abc123")
        # All abc123_*.json files removed
    """
    if not os.path.exists(STORE_PATH):
        return

    files = os.listdir(STORE_PATH)

    for f in files:
        if f.startswith(session_id):
            os.remove(
                os.path.join(STORE_PATH, f)
            )
