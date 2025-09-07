import streamlit as st

admin_page = st.Page("pages/Admin.py", title='Admin', icon=":material/person_add:")
chat_page = st.Page("pages/chat.py", title="Chats")

for_admin = [admin_page, chat_page]
page_dict = {}
def authenticated_menu():
    if "user" not in st.session_state:
        st.session_state["user"] = {"role": "student"}
    st.sidebar.title("General")
    st.sidebar.page_link("pages/chat.py", label="Chat")
    st.sidebar.page_link("pages/requests.py", label="Requests")
    st.sidebar.page_link("pages/courses.py", label="Your Courses")
    if st.session_state.user['role'] in['lecturer', 'admin']:
        st.sidebar.title("Courses")
        st.sidebar.page_link("pages/courses.py", label="Courses")
    if st.session_state.user['role'] in ["admin", "super-admin"]:

        st.sidebar.title("Admin")
        st.sidebar.page_link("pages/admin.py", label="Admin")
        st.sidebar.page_link("pages/manage_users.py", label="Manage Users")