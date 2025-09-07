import streamlit as st

def render():
    st.toast("No Files")
    with st.container(vertical_alignment="center", horizontal=True, horizontal_alignment='center'):
        st.image("assets/empty.png")