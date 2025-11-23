import streamlit as st
from utils.admin_functions import get_all_courses, add_course, delete_course, get_course
from components import empty_display
import pandas as pd

@st.dialog("Add Courses")
def add_courses():
    with st.form("Details"):
        course_name = st.text_input("Course name")
        course_code = st.text_input("Course code")
        coordinator = st.text_input("Coordinator")
        acad_year = st.number_input("Year", min_value=2025, help="Enter only the first year. For example, if AY25/26, enter 2025")
        sem = st.selectbox("Sem", options=["1", "2", "Special"])
        if st.form_submit_button("Submit"):
            course_details = {
                "course_name" :course_name,
                "course_code" : course_code,
                "coordinator" :coordinator,
                "acad_year":acad_year,
                "sem" : sem
            }
            add_course(course_details)
            st.session_state.courses = get_all_courses()
            st.rerun()
            return 1
@st.dialog("Delete Course")
def delete_courses():
    courses = st.session_state.courses
    course_map = {c.get("course_name"): c.get("_id") for c in courses}
    with st.form("Delete Courses"):
        chosen = st.multiselect(
            "Choose courses to delete",
            list(course_map.keys()),
            default = None
        )
        if st.form_submit_button("Delete"):
            delete_list = [course_map[name] for name in chosen]
            delete_course(delete_list)
            st.session_state.courses = get_all_courses()
            st.rerun()

@st.dialog("Edit Courses")
def edit_courses():
    courses = st.session_state.courses
    course_map = {c.get("course_name"): c.get("_id") for c in courses}
    option = st.selectbox(
        "Choose a course to edit",
        list(course_map.keys()),
    )
    course_id = course_map[option]
    current = get_course(course_id)
    if current and isinstance(current, dict):
        with st.form("Edit Courses"):
            course_name = st.text_input("Course Name", placeholder=current.get("course_name", ""))
            course_code = st.text_input("Course Code", placeholder=current.get("course_code", ""))
            if st.form_submit_button("Edit"):
                st.toast("editted")
        return
    else:
        st.write("There has been an error")

def render():
    try:
        if "courses" not in st.session_state:
            st.session_state.courses = get_all_courses()
        cols = st.columns(3)
        if cols[0].button("Add Course", key="add_course", width="stretch"):
            result = add_courses()
            if result:
                st.session_state.refresh = True
                st.rerun()
        if cols[1].button("Delete Course", key="delete_course", width="stretch"):
            delete_courses()

        if cols[2].button("Edit Course", key="edit_course", width="stretch"):
            edit_courses()

        courses = st.session_state.courses
        df = pd.DataFrame(courses)

        df.index +=1
        st.dataframe(df)
    except Exception as e:
        empty_display.render(courses, "course_table_admin")
    