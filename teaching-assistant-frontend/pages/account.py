import streamlit as st
from components.sidebar_menu import authenticated_menu
from utils.auth import require_login
from utils.styling import inject_custom_css
from datetime import datetime

inject_custom_css()
authenticated_menu()
require_login()
st.set_page_config(layout='wide')

st.title("Profile")
user = st.session_state.user
if not user:
    user = {'name': 'Unknown',
            'email': 'Unknown',
            'role': 'nil',
            'last_login': datetime.min}
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True, height=150):
        st.subheader("Name")
        st.markdown(f"###### {user.get('name', '')}")
    with st.container(border=True, height=150):
        st.subheader("Email")
        st.markdown(f"###### {user.get('email', '')}")
with col2:
    with st.container(border=True, height=150):
        st.subheader("Role")
        st.markdown(f"###### {user.get('role', '')}")
    with st.container(border=True, height=150):
        st.subheader("Last Login")
        last_login = user.get('last_login', '')
        if type(last_login) == datetime:
            formatted = last_login.strftime("%Y-%m-%d %H:%M:%S")
        st.write(f"###### {formatted}")