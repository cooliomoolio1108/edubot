import streamlit as st

def render(status:str, action:str):
    if status == "success":
        st.toast(action, icon='✅')
    else:
        st.toast(action, icon="❌")