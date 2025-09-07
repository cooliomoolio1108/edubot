import streamlit as st
import jwt, time
import os
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController
from typing import Callable

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

def header(jwt):
    return {"Authorization": f"Bearer {jwt}"}

def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        st.toast(icon="🚨",body="Session expired.")
    except jwt.InvalidTokenError:
        st.toast("Invalid token.")
    return None

def create_jwt(payload: dict):
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def bootstrap_and_persist():
    controller = CookieController()
    cookie = controller.get("login_token")
    refresh = controller.get("refresh_token")

    # Case 1: cookie is present but not yet in session
    if cookie and "login_token" not in st.session_state:
        claims = decode_jwt(cookie)
        if claims:
            st.session_state["login_token"] = cookie
            st.session_state["user"] = claims
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            controller.remove("login_token")
    # Case 2: cookie already persisted in session (normal flow)
    elif "login_token" in st.session_state:
        st.session_state["logged_in"] = True

def require_login(login_url="http://localhost:5050/auth/login"):
    bootstrap_and_persist()

    if not st.session_state.get("logged_in"):
        st.write("Navigate to Home and Login with SSO")
        st.stop()

    email = (st.session_state["user"].get("email") or "").lower()
    if not (email.endswith("@ntu.edu.sg") or email.endswith("@e.ntu.edu.sg")):
        st.error("Access denied: NTU only.")
        st.stop()

def require_role(allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = st.session_state.get("user", {})
            role = user.get("role", "student")
            if role not in allowed_roles:
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_token_expiry():
    st.session_state["show_refresh_login"] = True
    st.rerun()

def render_global_components(refresh_func: Callable[[], None]):
    if st.session_state.get("show_refresh_login", False):
        refresh_func()