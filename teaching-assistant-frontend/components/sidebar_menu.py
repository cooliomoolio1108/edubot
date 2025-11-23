import streamlit as st
from utils.auth import require_login
from. import sidebar_profile

page_dict = {}

def authenticated_menu(expand=False):
    require_login()
    with st.sidebar.expander("MENU", expanded=expand):
        if "user" not in st.session_state:
            st.session_state["user"] = {"role": "student"}
        sidebar_profile.render()
        st.title("General")
        st.page_link("pages/chat.py", label="💬 Chat")
        st.page_link("pages/requests.py", label="📨 Requests")
        st.page_link("pages/account.py", label="👤 Account")
        st.title("Courses")
        st.page_link("pages/courses.py", label="💻 Courses")
        if st.session_state.user['role'] in ["admin", "super-admin"]:
            st.title("Admin")
            st.page_link("pages/admin.py", label="🔰 Admin")
            st.page_link("pages/admin_requests.py", label="🛠️ Requests Management")
