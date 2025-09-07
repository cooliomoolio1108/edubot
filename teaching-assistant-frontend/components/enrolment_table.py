# import streamlit as st

# def render_enrolment():
#     st.title("Manage Enrolments")

import streamlit as st
import pandas as pd
from datetime import datetime

# --- Dummy enrolments ---
enrolments = [
    {
        "username": "Alice Tan",
        "course_name": "Multi-Disciplinary Project",
        "enrolled_at": datetime(2025, 9, 3, 10, 0),
        "is_active": True
    },
    {
        "username": "Benjamin Lee",
        "course_name": "Data Structures and Algorithms",
        "enrolled_at": datetime(2025, 9, 3, 10, 5),
        "is_active": True
    },
    {
        "username": "Cheryl Ng",
        "course_name": "Database Systems",
        "enrolled_at": datetime(2025, 9, 3, 10, 10),
        "is_active": False
    },
    {
        "username": "David Wong",
        "course_name": "Artificial Intelligence",
        "enrolled_at": datetime(2025, 9, 3, 10, 15),
        "is_active": True
    },
    {
        "username": "Elaine Lim",
        "course_name": "Software Engineering",
        "enrolled_at": datetime(2025, 9, 3, 10, 20),
        "is_active": True
    }
]
def render_enrolment():
    df = pd.DataFrame(enrolments)

    # --- Data Editor ---
    st.title("Manage Enrolments")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "username": st.column_config.TextColumn("User Name", required=True),
            "course_name": st.column_config.TextColumn("Course Name", required=True),
            "enrolled_at": st.column_config.DatetimeColumn(
                "Enrolment Date",
                format="YYYY-MM-DD HH:mm",
                step=60
            ),
            "is_active": st.column_config.SelectboxColumn(
                "Active Status",
                options=[True, False],
                default=True
            )
        }
    )

    # st.write("Edited enrolments:", edited_df)

