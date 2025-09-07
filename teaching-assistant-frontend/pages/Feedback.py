import streamlit as st
from streamlit_star_rating import st_star_rating
import os
import requests
from dotenv import load_dotenv
from utils.styling import inject_custom_css
from utils.auth import require_login
require_login()
load_dotenv()
API_URL = os.getenv("FLASK_API_URL") + "/feedback"

inject_custom_css()
st.title("Feedback")

if 'stars' not in st.session_state:
    st.session_state.stars = 0
if 'comment' not in st.session_state:
    st.session_state.comment = ""

with st.form(
    key="feedback",
    clear_on_submit=True,
    enter_to_submit=True,
    border=True
):
    stars = st_star_rating("Please rate your experience", maxValue=5, defaultValue=st.session_state.stars, key="rating")
    comment = st.text_area("Write your feedback:", value=st.session_state.comment)

    submitted = st.form_submit_button("Submit")
    if submitted:
        response = requests.post(API_URL, json={
            "stars": stars,
            "comments": comment
        })
        st.warning("Thank you for submitting!")
        st.session_state.stars = 0
        st.session_state.comment = ""