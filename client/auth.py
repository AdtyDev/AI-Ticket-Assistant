import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

def login( email: str,password:str):
    payload = {
        # "emp_id": emp_id,
        "email_id": email,
        "password": password
    }
    res = requests.post(f"{BASE_URL}/login", json=payload)
    return res


def init_session():
    defaults = {
        "session_id": None,
        "role": None,
        "name": None,
        "dept_id": None,
        "dept_name": None,
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_logged_in():
    return st.session_state.get("session_id") is not None

def logout():
    st.session_state.clear()
    st.rerun()


def render():
    init_session()
    # st.header("🔐 Login")

    # emp_id = st.text_input("Employee ID", key="login_emp")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if  not email or not password:
            st.warning("Please fill all fields")
            return
        
        res = login(email, password)

        if res.status_code == 200:
            data = res.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.role = data["role"]
            st.session_state.name = data["name"]
            st.session_state.emp_id = data.get("emp_id")
            st.session_state.dept_name = data.get("dept_name")
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
