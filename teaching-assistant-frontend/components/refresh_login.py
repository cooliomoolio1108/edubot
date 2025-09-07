import streamlit as st

@st.dialog("Refresh Login")
def refresh_login():
    st.write("Your login token has expired. Click to refresh login.")
    if st.button("Login via SSO", key="refresh_login"):
        st.success("Logging in")
        st.session_state["show_refresh_login"] = False