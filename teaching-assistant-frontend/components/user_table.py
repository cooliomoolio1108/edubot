import streamlit as st
import pandas as pd
from utils.admin_functions import get_all_users, delete_user, edit_user, add_users
from utils.debug import debug_session_state
from components import empty_display

def role_color(role: str) -> str:
    return {
        "admin": "red",
        "staff": "blue",
        "student": "green"
    }.get(role, "gray")

@st.dialog("Add Users", width="large")
def add_users_dialog():
    options = ["Add by CSV"]
    chosen = st.selectbox("Select Method", options, placeholder="Add By")
    if chosen == options[0]:
        uploaded = st.file_uploader("Choose a file", type='csv')
        if uploaded:
            df = pd.read_csv(uploaded)
            

def render_user_admin():
    flex = st.container()
    flex.write("# Manage Users")

    # Init session_state
    if "users" not in st.session_state:
        st.session_state.users = get_all_users()
    if "disabled" not in st.session_state:
        st.session_state.disabled = True
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    edit_mode = st.session_state.edit_mode
    user_data = st.session_state.users
    # Action buttons
    if user_data:
        if not edit_mode:
            col1, _, _ = st.columns(3)
            with col1:
                with st.container(horizontal=True):
                    if st.button("Edit Users", key='edit_mode_on', use_container_width=True, ):
                        st.session_state.disabled = False
                        st.session_state.edit_mode = True
                        st.rerun()
                    st.button("ⓘ", key='crud_help', type="tertiary", help="Press 'Edit' button to add, edit or delete users. Make sure to press 'Confirm Edits' to save them")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("❌", key='edit_mode_off', use_container_width=True):
                    st.session_state.disabled = True
                    st.session_state.edit_mode = False
                    st.rerun()
            with col2:
                if st.button("✅", key="update_users", use_container_width=True):
                    changes = st.session_state.changed
                    rawdata = st.session_state.users
                    for row_idx in changes["deleted_rows"]:
                        print("row_idx:", row_idx)
                        user_dict = rawdata[row_idx]
                        print("user_dict:",user_dict)
                        if isinstance(user_dict, dict):
                            user_oid = user_dict.get('_id', '')
                            delete_user(user_oid)
                    for key, items in changes["edited_rows"].items():
                        key_int = int(key)
                        user_dict = rawdata[key_int]
                        if isinstance(user_dict, dict):
                            user_id = user_dict.get('_id', '')
                            edit_user(user_id, items)
                    added = changes['added_rows']
                    if added and isinstance(added, list):
                        add_users(added)
                    st.session_state.disabled = True
                    st.session_state.edit_mode = False
                    st.session_state.users = users_df
                    st.rerun()
            with col3:
                if st.button("✚✚ by bulk", key='add_users', use_container_width=True):
                    add_users_dialog()
        needed_columns = ['name', 'email', 'is_active', 'role']
        df = pd.DataFrame(user_data)
        df.index += 1
        df = df[needed_columns]
        users_df = st.data_editor(
            df,
            key='changed',
            num_rows="dynamic",
            column_config={
                'name': st.column_config.Column("Name"),
                'email': st.column_config.Column('Email'),
                'is_active': st.column_config.SelectboxColumn(
                    'Active Status', options=[True, False], default=True
                )
            },
            disabled=st.session_state.disabled,
        )
    else:
        empty_display.render()

    debug_session_state()