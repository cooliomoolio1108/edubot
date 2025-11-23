# import streamlit as st
# from streamlit_pdf_viewer import pdf_viewer
# from utils.auth import decode_jwt

# def render():
#     if st.session_state.paramlist:
#         paramlist = st.session_state.paramlist
#     if paramlist:
#         for idx, p in enumerate(paramlist):
#             details = decode_jwt(p)
#             source = details.get("source", "")
#             key = source
#             st.write(details)
#             pdf_viewer(
#                 source,
#                 width=700,
#                 height=1000,
#                 zoom_level=1.2,                    # 120% zoom
#                 viewer_align="center",             # Center alignment
#                 show_page_separator=True,           # Show separators between pages
#                 key=f'source_{idx}'
#             )

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from utils.auth import decode_jwt
from utils.admin_functions import view_file
import streamlit.components.v1 as components

def render():
    st.title("📄 File Viewer")

    paramlist = st.session_state.get("paramlist", [])
    if not paramlist:
        st.info("No files available to view.")
        return

    for idx, p in enumerate(paramlist):
        try:
            details = decode_jwt(p)
        except Exception as e:
            st.error(f"Failed to decode file token: {e}")
            continue

        # Extract relevant fields
        source = details.get("source")
        name = details.get("name") or f"Document {idx+1}"

        if not source:
            st.warning(f"Missing 'source' in item {idx+1}. Skipping.")
            continue
        file_info = view_file(source)
        if not file_info or not file_info.get("url"):
            st.error(f"Failed to retrieve file from source: {source}")
            continue
        view_url = file_info["url"]
        viewer_url = f"https://docs.google.com/gview?embedded=true&url={view_url}"
        st.components.v1.iframe(viewer_url, height=900)
        # components.iframe(view_url, height=500, scrolling=True)
        # Display file info
        # with st.expander(f"📘 {name}", expanded=True):
        #     st.json(details)  # or st.write(details) if you prefer a simpler look

        #     # Render PDF viewer
        #     pdf_viewer(
        #         view_url,
        #         width=700,
        #         height=1000,
        #         zoom_level=1.2,          # 120% zoom
        #         viewer_align="center",   # Center alignment
        #         show_page_separator=True,
        #         key=f"pdf_{idx}"
        #     )