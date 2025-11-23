import streamlit as st
from components.dashboard_card import dashboard_card
from utils.admin_functions import get_all_courses
from utils.chat_functions import save_convo_id

# ---- Shared cards ----
def quick_actions():
    if st.button("➕ Start New Chat", width="stretch"):
        create_convo()
    st.button("📚 View My Courses", width="stretch")

def last_chat():
    st.write("💬 Last Chat: *'Explain topic X?'*")
    st.caption("2 hours ago")
    st.button("Resume Chat", width="stretch")

def recent_courses():
    courses = ["CS101", "MA202", "AI405"]  # replace with dynamic data
    for c in courses:
        st.link_button(c, f"/courses/{c}")

def request_course():
    st.write("Request Course Here")
def request_course_access():
    st.write("Request Course Access Here")

@st.dialog("Creating Conversation")
def create_convo():
    if "courses" not in st.session_state:
        st.session_state.courses = get_all_courses()
    if "conversations" not in st.session_state:
        st.session_state.conversations = {
            "title": "title",
            "messages": [],
            "title_updated": False,
            "course_id": ""
        }
    options = st.session_state.courses
    if options and isinstance(options, (list, set, tuple)):
        course_options = {
            f"{option['course_name']}": option['_id']  # Display title, store code
            for option in options
        }
        option = st.selectbox(
            "Choose a course for this conversation",
            course_options.keys(),
        )
        if option and st.page_link("pages/chat.py", label="💬 Chat"):
            st.session_state.create_new_convo = True
            title = "New Chat"
            user_id = st.session_state['user']['oid'] or 'nil'
            new_convo_id = save_convo_id(title, course_options[option])
            if new_convo_id:
                st.session_state.conversations[new_convo_id] = {
                    "title": title,
                    "messages": [],
                    "title_updated": False,
                    "course_id": course_options[option]
                }
                st.session_state.current_conversation = new_convo_id
            # st.page_link("pages/chat.py", label="💬 Chat")