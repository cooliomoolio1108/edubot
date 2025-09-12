import streamlit as st
import msal
import requests

query_params = st.query_params
if "code" in query_params:
    result = app.acquire_token_by_authorization_code(
        query_params["code"],
        scopes=["User.Read"],
        redirect_uri=config["redirect_uri"] + REDIRECT_PATH,
    )
    if "id_token_claims" in result:
        st.session_state["id_token"] = result["id_token_claims"]
        st.rerun()