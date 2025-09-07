import streamlit as st
import base64
from pathlib import Path

def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render():
    # --- Load image and apply CSS with opacity overlay ---
    img_path = Path("assets/background.png")  # change to your path
    img_base64 = get_base64_of_bin_file(img_path)

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: none; /* reset */
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url("data:image/jpg;base64,{img_base64}") no-repeat center center fixed;
            background-size: cover;
            opacity: 0.1;  /* 👈 only affects background */
            z-index: -1;   /* keep it behind everything */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )