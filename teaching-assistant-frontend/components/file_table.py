# import streamlit as st
# import os
# import pandas as pd
# from datetime import datetime
# import time
# from dotenv import load_dotenv
# from utils.admin_functions import get_files, upload_files, embed_files
# from components import empty_display
# # from streamlit_pdf_viewer import pdf_viewer
# # from . import filePreview

# def display_file(course):
#     st.markdown(
#         """
#         <style>
#         [data-testid="stLayoutWrapper"] {
#             background: rgb(255, 255, 255, 1);
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )
#     needed_columns = ['file_name', "file_size"]
#     course_id = course.get("_id", "")
#     files = get_files(course_id)
#     if files:
#         df = pd.DataFrame(files)

#         # Split into embedded / non-embedded
#         embedded = df[df["embedded"]].reset_index(drop=True)
#         nonembed = df[~df["embedded"]].reset_index(drop=True)

#         needed_columns = ["file_name", "file_size"]

#         st.subheader("📂 Embedded Files")
#         with st.container(border=True):
#             for _, row in embedded[needed_columns].iterrows():
#                 cols = st.columns([3, 1])
#                 cols[0].write(f"**{row['file_name']}**")
#                 cols[1].write(f"{row['file_size']} bytes")

#         st.subheader("📂 Non-Embedded Files")
#         with st.container(border=True):
#             for _, row in nonembed[needed_columns].iterrows():
#                 cols = st.columns([3, 1])
#                 cols[0].write(f"**{row['file_name']}**")
#                 cols[1].write(f"{row['file_size']} bytes")
#         # embedded_outdf = st.dataframe(embedded)
#         # nonembed_outdf = st.dataframe(nonembed)
#         # # Show as table with action buttons
#         # for i, row in embedded.iterrows():
#         #     with st.expander():
#         #         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         #         with col1:
#         #             st.write(f"**Uploaded by:** {row['uploaded_by']}")
#         #         with col2:
#         #             st.write(f"**Uploaded at:** {row['uploaded_at']}")
#         #         with col3:
#         #             st.write(f"**Embedded:** {'✅' if row['embedded'] else '❌'}")
#         #         with col4:
#         #             if st.button("📄 Unembed", key=f"unembed_{i}"):
#         #                 st.info(f"Simulate viewing: `{row['path']}`")
#         #         with col5:
#         #             if st.button("🗑️ Re-embed", key=f"reembed_{i}"):
#         #                 st.warning(f"Simulate deletion of `{row['file_name']}`")
#         #             # if st.download_button("⬇️ Download", data=open(row["path"], "rb").read(), file_name=row["file_name"]):
#         #             #     st.success(f"Downloaded `{row['file_name']}`")
#         #         with col6:
#         #             if st.button("🗑️ Delete", key=f"delete_{i}"):
#         #                 st.warning(f"Simulate deletion of `{row['file_name']}`")
#         #                 # Add DB/FS delete logic here
#         # st.write("Embedded Files")
#         # for i, row in embedded.iterrows():
#         #     with st.expander(f"{row['file_name']}"):
#         #         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         #         with col1:
#         #             st.write(f"**Uploaded by:** {row['uploaded_by']}")
#         #         with col2:
#         #             st.write(f"**Uploaded at:** {row['uploaded_at']}")
#         #         with col3:
#         #             st.write(f"**Embedded:** {'✅' if row['embedded'] else '❌'}")
#         #         with col4:
#         #             if st.button("📄 Unembed", key=f"unembed_{i}"):
#         #                 st.info(f"Simulate viewing: `{row['path']}`")
#         #         with col5:
#         #             if st.button("🗑️ Re-embed", key=f"reembed_{i}"):
#         #                 st.warning(f"Simulate deletion of `{row['file_name']}`")
#         #             # if st.download_button("⬇️ Download", data=open(row["path"], "rb").read(), file_name=row["file_name"]):
#         #             #     st.success(f"Downloaded `{row['file_name']}`")
#         #         with col6:
#         #             if st.button("🗑️ Delete", key=f"delete_{i}"):
#         #                 st.warning(f"Simulate deletion of `{row['file_name']}`")
#         #                 # Add DB/FS delete logic here
        
#         # st.write("Non-Embedded Files")
#         # for i, row in nonembed.iterrows():
#         #     with st.expander(f"{row['file_name']}"):
#         #         col1, col2, col3, col4, col5 = st.columns(5)
#         #         with col1:
#         #             st.write(f"**Uploaded by:** {row['uploaded_by']}")
#         #         with col2:
#         #             st.write(f"**Uploaded at:** {row['uploaded_at']}")
#         #         with col3:
#         #             st.write(f"**Embedded:** {'✅' if row['embedded'] else '❌'}")
#         #         with col4:
#         #             if st.button("📄 Embed", key=f"embed_{i}"):
#         #                 file_id = row['id']
#         #                 print('File IDs', file_id)
#         #                 reply = embed_files(file_id)
#         #                 if reply:
#         #                     fail = reply.get('failed_files')
#         #                     if fail:
#         #                         fail = fail[0]
#         #                         reason = fail.get('reason')
#         #                         st.warning(reason)
#         #                     else:
#         #                         st.success("✅ Embedding successful!")
#         #                     st.session_state.embedding_done = True
#         #                     time.sleep(2)
#         #                     st.rerun()
#         #                 else:
#         #                     st.error("❌ Failed to embed")
#         #         with col5:
#         #             if st.button("🗑️ Delete", key=f"delete_{i}"):
#         #                 st.warning(f"Simulate deletion of `{row['file_name']}`")
#         #                 # Add DB/FS delete logic here
#     else:
#         empty_display.render()