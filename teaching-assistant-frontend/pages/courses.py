import streamlit as st
from dotenv import load_dotenv
from utils.styling import inject_custom_css
from utils.admin_functions import get_all_courses, get_course
from utils.auth import require_login
from utils.config import COURSE_ROLE_TABS
from components import sidebar_menu, embed_components, course_details, background

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
    st.sidebar.write('---------')
role = st.session_state.user.get("role", "student")
# tabs = st.tabs(["Course Details", "Files Management", "Enrolled", "Analytics", "Vector Stores"], width='stretch')
tabs = st.tabs(COURSE_ROLE_TABS.get(role, []))
courseid = st.session_state.chosen_course
course = get_course(courseid)
if course:
    tab_idx = 0
    if "Course Details" in COURSE_ROLE_TABS[role]:
        with tabs[tab_idx]:
            course_details.render(course)
        tab_idx += 1

    if "Files Management" in COURSE_ROLE_TABS[role]:
        with tabs[tab_idx]:
            embed_components.upload_file(course)
            embed_components.display_file(course)
        tab_idx += 1

    if "Enrolled" in COURSE_ROLE_TABS[role]:
        with tabs[tab_idx]:
            st.write("Show enrolled students here…")
        tab_idx += 1

    if "Analytics" in COURSE_ROLE_TABS[role]:
        with tabs[tab_idx]:
            st.write("Show analytics here…")
        tab_idx += 1

    if "Vector Stores" in COURSE_ROLE_TABS[role]:
        with tabs[tab_idx]:
            st.write("Admin-only vector store management here…")
            embed_components.display_embeds(courseid)
else:
    st.write("NIL")