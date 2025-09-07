import streamlit as st
from utils.auth import require_role

@require_role(['admin'])
def dashboard_card(title: str, render_body, icon: str = None, color: str = "#1e1e2f"):
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #181d9b, #1e90ff);
            transition: transform 1s ease-in-out;
        ">
            <h3 style="margin: 0; font-size: 1.2rem; color: white;">
                {icon or ''} {title}
            </h3>
        """,
        unsafe_allow_html=True
    )

    # Render the body
    with st.container(border=False, height=200):
        render_body()

    # Close the div
    st.markdown("</div>", unsafe_allow_html=True)