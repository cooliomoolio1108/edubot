import streamlit as st
from. import sidebar_profile

page_dict = {}

def authenticated_menu():
    if "user" not in st.session_state:
        st.session_state["user"] = {"role": "student"}
    sidebar_profile.render()
    st.sidebar.title("General")
    st.sidebar.page_link("pages/chat.py", label="💬 Chat")
    st.sidebar.page_link("pages/requests.py", label="📨 Requests")
    st.sidebar.page_link("pages/account.py", label="👤 Account")
    if st.session_state.user['role'] in['lecturer', 'admin']:
        st.sidebar.title("Courses")
        st.sidebar.page_link("pages/courses.py", label="💻 Courses")
    if st.session_state.user['role'] in ["admin", "super-admin"]:
        st.sidebar.title("Admin")
        st.sidebar.page_link("pages/admin.py", label="🔰 Admin")
