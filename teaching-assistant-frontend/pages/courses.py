import streamlit as st
import os
from dotenv import load_dotenv
from utils.styling import inject_custom_css
from utils.admin_functions import get_all_courses, get_course
from utils.auth import require_login
from components import sidebar_menu, embed_components, course_details, background, file_table
from components.PromptEngineer import render

require_login()
load_dotenv()
st.set_page_config(page_title="Course Panel", layout="wide")
inject_custom_css()
sidebar_menu.authenticated_menu()
background.render()
    
if "upload_done" not in st.session_state:
    st.session_state.upload_done = False

st.write('# Your Courses')

if "courses" not in st.session_state:
    st.session_state.courses = get_all_courses()

if "chosen_course" not in st.session_state:
    st.session_state.chosen_course = ''

courses = st.session_state.courses

if isinstance(courses, list) and courses:
    st.sidebar.title("Courses")
    course_map = {c.get("course_name"): c.get("_id") for c in courses}

    option = st.sidebar.selectbox(
        "Courses", 
        options=list(course_map.keys()), 
        label_visibility="collapsed"
    )

    if option:
        st.session_state.chosen_course = course_map[option]


else:
    st.sidebar.write("No Courses")

tabs = st.tabs(["Course Details", "Files Management", "Enrolled", "Analytics", "Vector Stores"], width='stretch')
courseid = st.session_state.chosen_course
course = get_course(courseid)
if course:
    with tabs[0]:
        course_details.render(course)
    with tabs[1]:
        embed_components.upload_file(course)
        embed_components.display_file(course)
else:
    st.write("NIL")