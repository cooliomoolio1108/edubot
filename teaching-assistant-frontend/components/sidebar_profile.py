import streamlit as st

def render():
    col1, col2 = st.columns(2)
    with st.sidebar:
        st.header("Welcome User")
        st.page_link("Home.py", label="🏠 Home")