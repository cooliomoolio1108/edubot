import streamlit as st

def get_current_messages():
    """Return the list of messages for the current conversation."""
    conv_id = st.session_state.get("conversations")
    if conv_id is None:
        return []
    return conv_id