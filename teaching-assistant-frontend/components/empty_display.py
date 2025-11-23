import streamlit as st

def render(data: str, key: str):
    st.button(data, width='stretch', type='tertiary', key=key)
    st.toast("No Files")
    with st.container(vertical_alignment="center", horizontal=True, horizontal_alignment='center'):
        st.image("assets/empty.png")