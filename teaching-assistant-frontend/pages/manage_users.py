import streamlit as st
from utils.admin_functions import get_all_users, delete_user, edit_user
import pandas as pd
from utils.styling import inject_custom_css
from utils.auth import require_login
from components import sidebar_menu

st.set_page_config(page_title="Users Panel", layout="wide")
require_login()
inject_custom_css()
sidebar_menu.authenticated_menu()

if "users" not in st.session_state:
    users = get_all_users()
    st.session_state.users = users
if "disabled" not in st.session_state:
    st.session_state.disabled = True
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

def role_color(role):
    return {
        "admin": "red",
        "staff": "blue",
        "student": "green"
    }.get(role, "gray")


@st.dialog("Add Users", width="large")
def add_users():
    options = ["Add by CSV"]
    chosen = st.selectbox("Select Method", options, placeholder="Add By")
    if chosen == options[0]:
        uploaded = st.file_uploader("Choose a file", type='csv')
        if uploaded:
            df = pd.read_csv(uploaded)
            st.write(df)

@st.dialog("Delete Users", width='large')
def delete_users():
    st.write("delete")

st.title("Manage Users")

edit_mode = st.session_state.edit_mode
if not edit_mode:
    column1, nil1, nil2 = st.columns(3)
    with column1:
        if st.button("Edit Users", key='edit_mode_on', width='stretch'):
            st.session_state.disabled = False
            st.session_state.edit_mode = True
            st.rerun()
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Cancel Editing", key='edit_mode_off', width='stretch'):
            st.session_state.disabled = True
            st.session_state.edit_mode = False
            st.rerun()
    with col2:
        if st.button("Confirm Edits", key="update_users", width='stretch'):
            changes = st.session_state.changed
            rawdata = st.session_state.users
            for row_idx in changes["deleted_rows"]:
                user_dict = rawdata[row_idx]
                if isinstance(user_dict, dict):
                    user_oid = user_dict.get('oid', '')
                    delete_user(user_oid)
            for key, items in changes["edited_rows"].items():
                key_int = int(key)
                user_dict = rawdata[key_int]
                if isinstance(user_dict, dict):
                    user_oid = user_dict.get('oid', '')
                    edit_user(user_oid)
            st.session_state.disabled = True
            st.session_state.edit_mode = False
            st.rerun()
    with col3:
        if st.button("Add Users by Bulk", key='add_users', width='stretch'):
            add_users()
# st.selectbox("Add Users", ("Add by CSV", "Add Manually"), placeholder="Add users")
df = pd.DataFrame(st.session_state.users)
df.index +=1
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
disabled = st.session_state.disabled
users_df = st.data_editor(df, key='changed', num_rows="dynamic", column_config ={
    'created_at':st.column_config.DatetimeColumn("Date of Creation", format="D MMM YYYY, h:mm a"),
    'name': st.column_config.Column("Name"),
    'email': st.column_config.Column('Email'),
    'is_active':st.column_config.SelectboxColumn('Active Status', options=[True, False], default=True)
}, disabled=disabled)
st.write(st.session_state['changed'])
st.write(st.session_state.users)