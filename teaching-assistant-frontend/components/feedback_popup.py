import streamlit as st
from utils.chat_helpers import get_current_messages
from utils.admin_functions import add_feedback

def render_message(content):
    with st.container(border=True):
        st.subheader("Message chosen")
        st.markdown(content)

@st.dialog("Feedback Form",width='large')
def render(key, msg, convo_id):
    content = msg.get("content", "")
    if content:
        render_message(content)
    else:
        render_message(msg)
    with st.form(key=f"feedback_{key}"):
        subject = st.text_input("Subject", placeholder="Max 100 characters")
        rating = st.slider("Rate this chat", 1, 5, 3)
        comment = st.text_area("Any comments?")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            feedback = {
                "rating": rating,
                "comment": comment,
                "conversation_id": convo_id,
                "subject": subject
            }
            results = add_feedback(feedback)
            if results:
                st.success("Feedback submitted. Thank you!")
            else:
                st.error("Failed to submit feedback. Please try again.")
            st.rerun()
