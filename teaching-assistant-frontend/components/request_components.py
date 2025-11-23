import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from utils.admin_functions import process_to_df, get_feedback_summary
from utils.chat_helpers import stream_message

def set_current_issue(issue):
    st.session_state.current_issue = issue

def get_current_issue():
    return st.session_state.get("current_issue", None)

@st.dialog("Create Issue")
def create_issue(add_issues):
    categories = st.session_state.categories
    cat_map = {c.get("name", "-"): c["_id"] for c in categories}
    with st.form("Details"):
        cat = st.selectbox(
            "Choose an Issue Category",
            cat_map.keys()
            )
        title = st.text_input("Title", placeholder="Max 100 characters")
        desc = st.text_area("Description", placeholder="Max 200 characters")
        submitted = st.form_submit_button("Submit")
        if submitted:
            issue_detail = {
                "title": title,
                "desc": desc,
                "cat": cat_map[cat]
            }
            if add_issues(issue_detail):
                st.rerun()

@st.dialog("View Issue", width="large")
def view_issue():
    issue = get_current_issue()
    df = process_to_df(issue)
    st.dataframe(df)

def render_issues(item: dict, fields: list[str]):
    if item and isinstance(item, dict):
        issue_id = item.get("_id", "title")
        cols = st.columns(len(fields)+1)  # one col per field

        for col, field in zip(cols, fields):
            value = item.get(field, "")
            col.metric(label=field.capitalize(), value=value)

        # style all metric cards in row
        style_metric_cards(background_color="#ABABAB")
        with cols[-1]:
            if st.button("View", key=f"view_{issue_id}", width="stretch"):
                set_current_issue(item)
                view_issue()
                st.success("Viewed")
            if st.button("Update", key=f"update_{item.get("_id", "title")}", width="stretch"):
                st.success("Updated")
    else:
        st.warning("Invalid item received.")

def render_feedback(item: dict, fields: list[str]):
    if not item or not isinstance(item, dict):
        return
    
    feedback_id = item.get("_id", "content")

    with st.container(border=True):
        # Display each field as "Label: value"
        for field in fields:
            value = item.get(field, "")
            st.markdown(f"**{field.capitalize()}:** {value}")

        st.divider()

        # Simple action button
        if st.button("👀 View Feedback", key=f"view_{feedback_id}"):
            set_current_issue(item)
            view_issue()

def create_ai_summary():
    st.header("⊹ ࣪ ˖ AI Summary of Feedbacks")
    with st.container(border=True, height=200):
        if "fdbk_ai_sum" not in st.session_state:
            st.session_state.fdbk_ai_sum = None
        
        ai_feedback = st.session_state.fdbk_ai_sum
        if not ai_feedback:
            summary = get_feedback_summary()
            st.session_state.fdbk_ai_sum = summary
            stream_message(summary, "new", 0.8)
            st.rerun()
        else:
            st.markdown(ai_feedback)


    