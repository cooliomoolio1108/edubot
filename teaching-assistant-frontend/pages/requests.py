import streamlit as st
from components import sidebar_menu, request_components
from utils.auth import require_login
from dotenv import load_dotenv
from utils.styling import inject_custom_css
from utils.admin_functions import get_feedbacks, get_issues, add_issues, get_categories

require_login()
load_dotenv()
st.set_page_config(page_title="Course Panel", layout="wide")
inject_custom_css()
sidebar_menu.authenticated_menu()

st.title("Requests")
tabs = st.tabs(["Open Issues", "Closed Issues", "Feedback"])

if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = get_feedbacks()

if "issues" not in st.session_state:
    st.session_state.issues = get_issues()

if "categories" not in st.session_state:
    st.session_state.categories = get_categories()

with st.sidebar:
    st.write('--------')
    if st.button("Create Issue", width="stretch", type='primary'):
        request_components.create_issue(add_issues)

with tabs[0]:
    st.header("Your Issues")
    issues = st.session_state.issues
    with st.container(key="issue_list", border=True):
        for i in issues:
            request_components.render_issues(i, ["_id", "title"])

# with tabs[2]:
    # st.header("Feedback")
    # request_components.create_ai_summary()
    # feedbacks = st.session_state.feedbacks
    # with st.container(key="feedback_list", border=True):
    #     for f in feedbacks:
    #         request_components.render_feedback(f, ["_id", "rating", "subject","comment"])
