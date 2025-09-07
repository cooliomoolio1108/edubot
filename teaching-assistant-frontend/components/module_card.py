import streamlit as st
from streamlit_card import card
import pathlib

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = pathlib.Path("assets/styles.css")
load_css(css_path)

def show_card(image_path, title, text, key):
    if card(
        title=title, text=text, image=image_path, key=key,
        styles={
            "card": {
                "margin": "10px"
            }
        }):
        return