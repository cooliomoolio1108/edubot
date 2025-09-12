import streamlit as st
from utils.chat_helpers import get_current_messages

def render_message(content):
    with st.container(border=True):
        st.subheader("Message chosen")
        st.markdown(content)
@st.dialog("Feedback Form",width='large')
def render(key, msg):
    content = msg.get("content", "")
    if content:
        render_message(content)
    else:
        render_message(msg)
    with st.form(key=f"feedback_{key}"):
        stars = st.slider("Rate this course", 1, 5, 3)
        comments = st.text_area("Any comments?")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.success(f"Thanks for rating {stars} stars! Comment: {comments}")
