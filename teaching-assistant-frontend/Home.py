import streamlit as st
from utils.auth import decode_jwt, bootstrap_and_persist
from utils.admin_functions import get_user
from utils.styling import inject_custom_css
from utils.debug import debug_session_state
from dotenv import load_dotenv
import st_cookie
from pathlib import Path
import base64
from components.sidebar_menu import authenticated_menu
from components.dashboard_card import dashboard_card
from components import dashboard_cards_function as card
from components import background
import os

# --- Setup ---
if "user" not in st.session_state:
    st.session_state["user"] = {"role": "student"}
st.set_page_config(
    page_title="Home",
    page_icon="home",
    layout="wide",
)
st_cookie.apply()
inject_custom_css()
bootstrap_and_persist()
load_dotenv()
authenticated_menu()
background.render()

# --- Helpers ---
def get_base64_of_bin_file(bin_file: Path) -> str:
    """Convert local image to base64 for embedding in CSS."""
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()
    
# Path to local image
img_path = Path("assets/chatbot.png")
img_base64 = get_base64_of_bin_file(img_path)

# --- Login Warning Dialog ---
@st.dialog("⚠ Login Required")
def show_login_warning():
    st.write("You are about to log in via NTU SSO. Continue?")
    c1, c2 = st.columns([1, 1])

    with c1:
        if st.button("✅ Yes, log me in"):
            st.markdown(
                f"<meta http-equiv='refresh' content='0; url={FLASK_LOGIN}'>",
                unsafe_allow_html=True,
            )
    with c2:
        if st.button("❌ Cancel"):
            st.rerun()

FLASK_LOGIN = os.getenv("FLASK_LOGIN")

# with col2:
if st.session_state.get("logged_in"):
    oid = st.session_state["user"]["oid"] or ""
    user = get_user(oid, by="oid")
    st.session_state["user"]["role"] = user.get("role", "nil")
    role = st.session_state["user"]["role"]
    st.write(user)

    st.markdown(
        f"# Welcome, <span style='color:green'>{st.session_state['user']['name']}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(f"`{st.session_state.user.get('role', 'student')}`")
    # if st.button("Choose your role"):
    #     current = st.session_state.user['role']
    #     print(current)
    #     if current == 'student':
    #         st.session_state.user['role'] = 'admin'
    #     else:
    #         st.session_state.user['role'] = 'student'
    col1, col2 = st.columns(2)
    with col1: dashboard_card("Quick Actions", card.quick_actions, icon="⚡", color="#20294f")
    with col2: dashboard_card("Last Chat", card.last_chat, icon="💬", color="#20294f")


else:
    bg_path = Path("assets/4882066.jpg")
    bg_base64 = get_base64_of_bin_file(bg_path)
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    logo1, logo2, logo3 = st.columns(3)
    with logo2:
        st.image(img_path)
    # Put the Streamlit button *after* the styled block
    but1, but2, but3 = st.columns(3)
    with but2:
        left, center, right = st.columns([1,1,1])
        with center:
            if st.button("SSO LOGIN ->"):
                show_login_warning()



# Debugging (optional)
# debug_session_state()