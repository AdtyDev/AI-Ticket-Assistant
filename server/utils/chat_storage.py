import json
import os

STORE_PATH = "server/chat_store"



# Internal helper
def _file_path(session_id, conv_id):
    return f"{STORE_PATH}/{session_id}_{conv_id}.json"



# Save message
def save_message(session_id, conv_id, role, content):

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

    path = _file_path(session_id, conv_id)

    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        return json.load(f)


# List conversations

def list_conversations(session_id):

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

    if not os.path.exists(STORE_PATH):
        return

    files = os.listdir(STORE_PATH)

    for f in files:
        if f.startswith(session_id):
            os.remove(
                os.path.join(STORE_PATH, f)
            )
