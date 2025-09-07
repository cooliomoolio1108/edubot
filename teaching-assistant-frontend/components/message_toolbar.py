import streamlit as st
from . import preview_popup

@st.dialog("View Source", width='large')
def show_files():
    # link = os.getenv("STREAMLIT_URL") + '/View_Files'
    # st.link_button(label="click", url=link)
    preview_popup.render()

def render(idx):
    col1, col2, col3, col4 = st.columns([1,1,20,20])
    with col1:
        if st.button("⭐", key=f'feedback_{idx}', type='tertiary', help="Help us improve replies! Leave a Feedback!"):
            st.write("feedback given")
    with col2:
        if st.button('📝', key=f'sources_{idx}', type='tertiary',help="Click me to view sources mentioned in the assistant's reply"):
            show_files()