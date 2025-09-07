# debug_session.py
import streamlit as st
import json

def debug_session_state(expand=True):
    """Print all current session_state keys and values in Streamlit."""
    st.subheader("🔍 Session State Debug")
    if not st.session_state:
        st.info("Session state is currently empty.")
        return
    
    # Render as collapsible expander for neatness
    with st.expander("View session_state content", expanded=expand):
        for key, value in st.session_state.items():
            try:
                serialized = json.dumps(value, default=str, indent=2, ensure_ascii=False)
            except TypeError:
                serialized = str(value)
            
            st.markdown(f"**{key}**:")
            st.code(serialized, language="json")
