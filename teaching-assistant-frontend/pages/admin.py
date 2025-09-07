import streamlit as st
from components import sidebar_menu
from utils.auth import require_login
from dotenv import load_dotenv
from utils.styling import inject_custom_css
from components.dashboard_card import dashboard_card
from components import dashboard_cards_function as card
from components import user_table, enrolment_table

require_login()
load_dotenv()
st.set_page_config(page_title="Course Panel", layout="wide")
inject_custom_css()
sidebar_menu.authenticated_menu()

st.set_page_config(layout='wide')
st.title("Admin")

st.markdown(
    """
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] p {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
tabs = st.tabs(["Users", "Enrollments", "Courses", "Files", "Conversations"], width='stretch')

with tabs[0]:
    user_table.render_user_admin()
with tabs[1]:
    enrolment_table.render_enrolment()