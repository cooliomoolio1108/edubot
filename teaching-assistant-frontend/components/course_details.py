import streamlit as st
from typing import Dict
from utils.admin_functions import get_course
from streamlit_extras.metric_cards import style_metric_cards

def render(course: dict):
    st.sidebar.markdown('-----------')
    if course and isinstance(course, dict):
        details = course
        col1, col2= st.columns(2)

        col1.metric(label="Course Name", value=details.get("course_name", ""))
        col1.metric(label="Course Code", value=details.get("course_code", ""))
        col2.metric(label="Semester", value=details.get("sem", ""))
        col2.metric(label="coordinator", value=details.get("coordinator", ""))
        style_metric_cards(background_color="#ABABAB")
    else:
        st.write("Course Failed to Load!")