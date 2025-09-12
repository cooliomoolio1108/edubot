import streamlit as st
import os
import pandas as pd
from datetime import datetime
import time
from dotenv import load_dotenv
from utils.admin_functions import get_files, upload_files, embed_file, delete_files, get_embeds
from utils.auth import handle_token_expiry, render_global_components
# from streamlit_pdf_viewer import pdf_viewer
# from . import filePreview
from . import refresh_login, empty_display
from utils.debug import debug_session_state

load_dotenv()
if "upload_done" not in st.session_state:
    st.session_state.upload_done = False
if "embedding_done" not in st.session_state:
    st.session_state.embedding_done = False

def render_pdf():
    st.image("assets/pdf.svg")

def upload_file(course):
    course_name = course.get("course_name", "")
    course_id = course.get("_id", "")
    st.write(f'### Files')
    if not st.session_state.upload_done:
        with st.container():
            uploaded_files = st.file_uploader(
                f'Upload Files for `{course_name}`', accept_multiple_files=True
            )
        if uploaded_files:
            st.write(f"Detected {len(uploaded_files)} file(s).")
            for uploaded_file in uploaded_files:
                files = {
                    "file": (uploaded_file.name, uploaded_file, "application/pdf"),
                    "course_id": course_id
                }
                data = {
                    "file_name": uploaded_file.name,
                    "path": "/test",
                    "uploaded_by": st.session_state.get("username", "unknown"),
                    "course_id": course_id,
                    "file_size": uploaded_file.size,
                    "type": uploaded_file.type
                }
                response = upload_files(data, files)
            st.session_state.upload_done = True
            st.rerun()
    else:
        st.info("✅ Documents successfully uploaded and processed.")
        if st.button("Upload more"):
            st.session_state.upload_done = False
            st.rerun()

def display_file(course):
    needed_columns = ['file_name', "file_size", "_id"]
    course_id = course.get("_id", "")
    files = get_files(course_id)
    if files:
        df = pd.DataFrame(files)

        # Split into embedded / non-embedded
        embedded = df[df["embedded"]].reset_index(drop=True)
        nonembed = df[~df["embedded"]].reset_index(drop=True)

        st.subheader("📂 Embedded Files")
        with st.container(border=True, height=300):
            cols = st.columns([3,1,1,1])
            cols[0].write(f"`File name`")
            cols[1].write(f"`File size`")
            for _, row in embedded[needed_columns].iterrows():
                cols = st.columns([3,1,1,1])
                cols[0].write(f"**{row['file_name']}**")
                cols[1].write(f"{row['file_size']} bytes")
                if cols[2].button("Un-embed", key=f"unembed_y_idx{_}", width='stretch'):
                    st.toast("Unembedded!")
                if cols[3].button("Delete", key=f"delete_y_idx{_}", width='stretch'):
                    result = delete_files(row["_id"])

        st.subheader("📂 Non-Embedded Files")
        with st.container(border=True, height=300):
            cols = st.columns([3,1,1,1])
            cols[0].write(f"`File name`")
            cols[1].write(f"`File size`")
            for _, row in nonembed[needed_columns].iterrows():
                cols = st.columns([3,1,1,1])
                cols[0].write(f"**{row['file_name']}**")
                cols[1].write(f"{row['file_size']} bytes")
                if cols[2].button("Embed", key=f"embed_n_idx{_}", width='stretch'):
                    st.toast("Embedding..")
                    result = embed_file(row['_id'])
                    # st.rerun()
                if cols[3].button("Delete", key=f"delete_n_idx{_}", width='stretch'):
                    result = delete_files(row["_id"])
                    time.sleep(3)
                    st.rerun()
    else:
        empty_display.render()