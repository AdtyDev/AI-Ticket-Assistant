
import os
import uuid
import requests
import streamlit as st
import auth

API_URL = os.getenv("ASSISTANT_API_URL", "http://localhost:8001/assistant/chat")
HISTORY_URL = "http://localhost:8001/history"

def fetch_conversations():
    headers = {
        "X-SESSION-ID": st.session_state.session_id
    }

    res = requests.get(
        HISTORY_URL,
        headers=headers
    )

    if res.status_code == 200:
        return res.json()

    return []


def load_conversation(conv_id):
    headers = {
        "X-SESSION-ID": st.session_state.session_id
    }

    res = requests.get(
        f"{HISTORY_URL}/{conv_id}",
        headers=headers
    )

    if res.status_code == 200:
        return res.json()

    return []



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

    st.divider()
    st.subheader("📜 Chat History")

    convs = fetch_conversations()

    for c in convs:
        if st.button(c):
            st.session_state.conv_id = c
            st.session_state.history = load_conversation(c)
            st.rerun()




if "conv_id" not in st.session_state:
    st.session_state.conv_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

def display_history():
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
        
display_history()


user_input = st.chat_input("Ask me anything about tickets…", disabled=st.session_state.is_processing)

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.is_processing = True
    st.rerun()

if st.session_state.is_processing:


    last_msg = st.session_state.history[-1]
    if last_msg["role"] == "user":

    

    # Call the FastAPI endpoint
        payload = {"conversation_id": st.session_state.conv_id, "message": last_msg["content"]}
        

        headers = {
            "X-SESSION-ID": st.session_state.session_id
        }
        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    resp = requests.post(API_URL, json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    answer = data["answer"]
        except Exception as e:
            answer = f"❗️ **Error:** {e}"
            
        
        
        st.session_state.history.append({"role": "assistant", "content": answer})
        
        st.session_state.is_processing = False
        st.rerun()