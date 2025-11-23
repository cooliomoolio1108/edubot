import streamlit as st
import pandas as pd
from components import sidebar_menu
from components import empty_display, request_components
from utils.auth import require_login
from dotenv import load_dotenv
from utils.styling import inject_custom_css
from utils.admin_functions import get_categories, add_categories, delete_categories

require_login()
load_dotenv()
st.set_page_config(page_title="Course Panel", layout="wide")
inject_custom_css()
sidebar_menu.authenticated_menu()
st.title("Requests Management")

def refresh_cat():
    st.session_state.req_cat = get_categories()

def color_swatch(val):
    return f"background-color: {val}; color: {val}" if pd.notna(val) else ""

@st.dialog("Add Categories for Requests")
def add_cat():
    with st.form("Details"):
        name = st.text_input("Name")
        desc = st.text_input("Description")
        color = st.color_picker("Color")
        if st.form_submit_button("Submit"):
            cat_data = {
                "name" :name,
                "desc" : desc,
                "color": color
            }
            add_categories(cat_data)
            refresh_cat()
            st.rerun()
            return 1
        
@st.dialog("Add Categories for Requests")
def deactivate_cat(categories):
    cat_map = {c.get("name"): c.get("_id") for c in categories}
    with st.form("Delete Courses"):
        chosen = st.multiselect(
            "Choose courses to delete",
            list(cat_map.keys()),
            default = None
        )
        if st.form_submit_button("Delete"):
            ids = [cat_map[name] for name in chosen]
            delete_categories(ids)
            refresh_cat()
            st.rerun()
        
if "req_cat" not in st.session_state:
    refresh_cat()

tabs = st.tabs(["All Requests", "Request Categories Management", "Feedback Summary"])
with st.sidebar:
    st.write('--------')

with tabs[0]:
    st.header("Open Requests")

with tabs[1]:
    st.header("Manage Categories")
    categories = st.session_state.req_cat
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Categories", width="stretch"):
            add_cat()
    with col2:
        if st.button("Deactivate Categories", width="stretch"):
            deactivate_cat(categories)
    if categories:
        df = pd.DataFrame(categories)
        df.index += 1
        styled_df = df.style.applymap(color_swatch, subset=["color"])
        st.dataframe(styled_df, width="stretch")
    else:
        empty_display.render()
with tabs[2]:
    if "fdbk_ai_sum" not in st.session_state:
        st.session_state.fdbk_ai_sum = ""
    ai_feedback = st.session_state.fdbk_ai_sum
    if not ai_feedback:
        request_components.create_ai_summary()
    else:
        st.header("⊹ ࣪ ˖ AI Summary of Feedbacks")
        with st.container(border=True, height=200):
            st.write(ai_feedback)