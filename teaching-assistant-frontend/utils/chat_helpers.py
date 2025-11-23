import streamlit as st
import time
import re

def convert_to_latex(text: str) -> str:
    # Convert block equations \[...\] → $$...$$
    text = re.sub(r"\\\[(.+?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    # Convert inline equations \(...\) → $...$
    text = re.sub(r"\\\((.+?)\\\)", r"$\1$", text, flags=re.DOTALL)
    return text

def stream_message(text, mode, speed=0.01):
    placeholder = st.empty()
    accumulated = ""
    for chunk in text.split(" "):
        if mode == 'new':
            accumulated += chunk + " "
            placeholder.markdown(convert_to_latex(accumulated), unsafe_allow_html=True)
            time.sleep(0.01)  # simulate streaming
        else:
            accumulated += chunk + " "
            placeholder.markdown(convert_to_latex(accumulated), unsafe_allow_html=True)

def get_current_messages():
    """Return the list of messages for the current conversation."""
    conv_id = st.session_state.get("conversations")
    if conv_id is None:
        return []
    return conv_id

def get_course_name(course_id, courses):
    for c in courses:
        if c.get("_id") == course_id:
            return c.get("course_name", "")
    return ""
