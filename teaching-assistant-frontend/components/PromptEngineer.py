import streamlit as st
from utils.admin_functions import get_prompts
from utils.styling import inject_custom_css

def render():
    inject_custom_css()
    st.set_page_config(layout="wide")
    if "prompts" not in st.session_state:
        prompts = get_prompts()
        st.session_state.prompts = prompts

    if 'current_prompt' not in st.session_state:
        st.session_state.current_prompt = {}
    
    if 'prompt_editable' not in st.session_state:
        st.session_state.prompt_editable = False

    if st.session_state.prompts:
        toprint = st.session_state.prompts
        with st.sidebar:
            st.markdown(f'# Prompt Templates')
            for content in toprint:
                sidecols1, sidecols2 = st.columns([7,1])
                title = content.get("name", "")
                prompt_id = content.get("_id", "")
                with sidecols1:
                    if st.button(title, key=prompt_id):
                        st.session_state.current_prompt = content
                        editable = st.session_state.prompt_editable
                with sidecols2:
                    popover = st.popover("")
                    
    if st.session_state.current_prompt:
        current_prompt = st.session_state.current_prompt
        st.markdown(f"## {current_prompt.get('name', 'Unknown')}")
        editable = st.session_state.prompt_editable
        if not editable:
            if st.button("✎", key="edit_prompt_button_on"):
                st.session_state.prompt_editable = True
                st.rerun()
        else:
            if st.button("❌", key="edit_prompt_button_off"):
                st.session_state.prompt_editable = False
                st.rerun()
        with st.form("edit_prompt" if editable else "view_prompt"):
            cols1, cols2 = st.columns(2)
            with cols1:
                name = st.text_area("Name", value=current_prompt.get("name", ""), disabled=not editable, height="content")
                course_id = st.text_area("Course", value=current_prompt.get("course_id", ""), disabled=not editable, height="content")
                course_breakdown = st.text_area("Course Details", value=current_prompt.get("course_breakdown", ""), disabled=not editable, height="content")
            with cols2:
                system_template = st.text_area("System Template", value=current_prompt.get("system_template", ""), disabled=not editable, height="content")
                human_template = st.text_area("Human Template", value=current_prompt.get("human_template", ""), disabled=not editable, height="content")
            if editable:
                submitted = st.form_submit_button("Submit")
                st.session_state.editable = False
            else:
                st.form_submit_button("Click edit icon to edit", disabled=True)