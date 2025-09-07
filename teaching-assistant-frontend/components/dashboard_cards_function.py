import streamlit as st
from components.dashboard_card import dashboard_card

# ---- Shared cards ----
def quick_actions():
    st.button("➕ Start New Chat", use_container_width=True)
    st.button("📚 View My Courses", use_container_width=True)

def last_chat():
    st.write("💬 Last Chat: *'Explain topic X?'*")
    st.caption("2 hours ago")
    st.button("Resume Chat", use_container_width=True)

def recent_courses():
    courses = ["CS101", "MA202", "AI405"]  # replace with dynamic data
    for c in courses:
        st.link_button(c, f"/courses/{c}")

def request_course():
    st.write("Request Course Here")
def request_course_access():
    st.write("Request Course Access Here")