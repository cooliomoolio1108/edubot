import streamlit as st
from components import course_details
from typing import Any

def render(datalist: list[dict[str, Any]]) -> str | None:
    if not datalist:
        st.info("No courses available.")
        return None

    for data in datalist:
        if not isinstance(data, dict):
            continue  # skip invalid entries

        course_id = data.get("id")
        course_name = data.get("course_name", "Untitled")
        course_code = data.get("course_code", "N/A")
        coordinator = data.get("coordinator", "Unknown")
        status = data.get("is_active", False)
        if status == True:
            status = 'Active'
        else:
            status = 'Inactive'

        with st.container(border=True, vertical_alignment="center", horizontal=True, horizontal_alignment='distribute'):
            st.metric(label=f"{course_code}", value=f"📘 {course_name}")
            st.metric(label=f"👤 Instructor", value=f" {coordinator}")
            st.badge(f"Status: {status}")
            if st.button("Manage", key=f'course_{course_id}'):
                st.query_params.update({"course_id": course_id})
                return course_id

    return None
