# streamlit_app.py
import os
import uuid
import requests
import streamlit as st
import auth

API_URL = os.getenv("ASSISTANT_API_URL", "http://localhost:8001/assistant/chat")

st.title("🤖 CRM Assistant")

if not auth.is_logged_in():
    auth.render()
    st.stop()


with st.sidebar:
    st.title("Smart Support Desk")
    st.write(f"Emp ID: {st.session_state.emp_id}")
    st.write(f"👤 {st.session_state.name}")
    st.write(f"Role: {st.session_state.role}")
    st.write(f"Department: {st.session_state.dept_name}")

    if st.button("Logout"):
        auth.logout()



if "conv_id" not in st.session_state:
    st.session_state.conv_id = str(uuid.uuid4())
    st.session_state.history = []   # list of dict {role, content}

# if "session_id" not in st.session_state:
#     st.warning("⚠️ Please login first")
#     auth.render()

def display_history():
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

display_history()

user_input = st.chat_input("Ask me anything about tickets…")

if user_input:
    # Append user message locally
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Call the FastAPI endpoint
    payload = {"conversation_id": st.session_state.conv_id, "message": user_input}

    headers = {
        "X-SESSION-ID": st.session_state.session_id
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        answer = data["answer"]
    except Exception as e:
        answer = f"❗️ **Error:** {e}"

    # Append assistant message locally
    st.session_state.history.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)