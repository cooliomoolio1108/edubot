import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from utils.auth import decode_jwt

if st.session_state.paramlist:
    paramlist = st.session_state.paramlist
if paramlist:
    for idx, p in enumerate(paramlist):
        details = decode_jwt(p)
        source = details.get("source", "")
        key = source
        st.write(details)
        pdf_viewer(
            source,
            width=700,
            height=1000,
            zoom_level=1.2,                    # 120% zoom
            viewer_align="center",             # Center alignment
            show_page_separator=True,           # Show separators between pages
            key=f'source_{idx}'
        )