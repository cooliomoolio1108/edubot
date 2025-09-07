import streamlit as st
from utils.admin_functions import get_all_users
import pandas as pd

def render():
    if "users" not in st.session_state:
        users = get_all_users()
        print(users)
    st.subheader("Manage Users")
    st.write("Create, update, or delete Users.")
    def role_color(role):
        return {
            "admin": "red",
            "staff": "blue",
            "student": "green"
        }.get(role, "gray")

    st.title("👥 User Directory")
    columns_map = {
        'username': 'Username',
        'email': 'Email',
        'role': 'Role',
        'is_active':'Active Status',
        'created_at': 'Date of Creation'
    }
    columns_needed = ['Username','Email','Role','Active Status','Date of Creation']
    df = pd.DataFrame(users)
    df.rename(columns=columns_map, inplace=True,)
    df = df[columns_needed]
    df.index +=1
    df["Date of Creation"] = pd.to_datetime(df["Date of Creation"], errors="coerce")
    users_df = st.data_editor(df, num_rows="dynamic", column_config ={
                  'Date of Creation':st.column_config.DatetimeColumn(format="D MMM YYYY, h:mm a")
              })