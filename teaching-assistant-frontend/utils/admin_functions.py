import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from components import toast
from components.refresh_login import refresh_login
from utils.auth import handle_token_expiry, render_global_components
from utils.api_client import header, api_get, get_headers

load_dotenv()
MSG_API_URL = os.getenv("FLASK_API_URL") + "/message"
CONVO_API_URL = os.getenv("FLASK_API_URL") + "/conversation"
GPT_API_URL = os.getenv("FLASK_API_URL") + "/chat"
FDBK_API_URL = os.getenv("FLASK_API_URL") + "/feedback"
TITLE_API_URL = os.getenv("FLASK_API_URL") + "/generate_title"
USER_API_URL = os.getenv("FLASK_API_URL") + "/users"
COURSE_API_URL = os.getenv("FLASK_API_URL") + "/courses"
FILE_API_URL = os.getenv("FLASK_API_URL") + "/files"
EMBED_API_URL = os.getenv("FLASK_API_URL") + "/files/embed"
PRMPT_API_URL = os.getenv("FLASK_API_URL") + "/prompt"
REQ_API_URL = os.getenv("FLASK_API_URL") + "/request"

def process_to_df(issue: dict) -> pd.DataFrame:
    if not issue:
        pd.set_option("display.max_colwidth", None)
        return pd.DataFrame(columns=["Field", "Value"])
    return pd.DataFrame(issue.items(), columns=["Field", "Value"])

def process_json(resp, action: str, by: str = "single"):
    status_code = resp.status_code
    try:
        payload = resp.json()
    except Exception:
        return None

    status = payload.get("status")
    information = payload.get("data") if status == "success" else payload.get("reason", "")

    # --- Success (200 OK) ---
    if status_code == 200 and status == "success":
        if action != "nil":
            toast.render(status, information)
        return payload.get("data", {} if by == "single" else [])

    # --- Not Found (404) ---
    elif status_code == 404 and status == "fail":
        if action != "nil":
            toast.render(status, "Not Found")
        return {} if by == "single" else []

    # --- Validation / Client error (400) ---
    elif status_code == 400 and status == "fail":
        toast.render(status, information)
        return {} if by == "single" else []

    # --- Server error (500) ---
    elif status_code == 500 and status == "error":
        toast.render(status, information or "Internal Server Error")
        return None

    # --- Expired token special case ---
    elif status_code == 401 and information == "Token expired.":
        toast.render(status, information or "Internal Server Error")
        return information

    # --- Fallback ---
    else:
        toast.render("error", f"Unexpected: {information},{status_code}")
        return information

#cleaned
def get_all_users():
    headers = get_headers()
    try:
        response = requests.get(USER_API_URL, headers=headers)
        return process_json(response, "nil", "many")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"❌ Request failed: {req_err}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

#cleaned
def add_users(addedusers):
    headers = get_headers()
    try:
        response = requests.post(f"{USER_API_URL}", json=addedusers, headers=headers)
        return process_json(response, "Add Success")

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

#cleaned
def delete_user(id):
    headers = get_headers()
    try:
        response = requests.delete(f"{USER_API_URL}/{id}", headers=headers)
        return process_json(response, "Delete Success")

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

#cleaned
def get_user(identifier: str, by: str = "id"):
    headers = get_headers()
    try:
        if by == "oid":
            url = f"{USER_API_URL}/oid/{identifier}"
        else:
            url = f"{USER_API_URL}/{identifier}"

        response = requests.get(url, headers=headers)
        return process_json(response, "nil")

    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"❌ Request failed: {req_err}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

#cleaned
def edit_user(id, edits):
    try:
        response = requests.put(f"{USER_API_URL}/{id}", json={"edits": edits}, headers=headers)
        return process_json(response, "User(s) edited")

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

#cleaned
def get_all_courses():
    headers = get_headers()
    try:
        response = requests.get(COURSE_API_URL, headers=headers)
        return process_json(response, "nil", "many")
    
    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"❌ Request failed: {req_err}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

#cleaned
def get_course(id):
    headers = get_headers()
    try:
        url = COURSE_API_URL + f'/{id}'
        response = requests.get(url, headers=headers)
        return process_json(response, "nil", ",many")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def add_course(course_details):
    headers = get_headers()
    try:
        response = requests.post(COURSE_API_URL, json=course_details, headers=headers)
        return process_json(response, "Added")
    except Exception as e:
        st.error(e)

def delete_course(course_ids):
    headers = get_headers()
    try:
        response = requests.delete(COURSE_API_URL, json=course_ids, headers=headers)
        return process_json(response, "Deleted")
    except Exception as e:
        st.error(e)

def edit_course(edits):
    headers = get_headers()
    try:
        response = requests.put(COURSE_API_URL, json=edits, headers=headers)
        return process_json(response, "Edited")
    except Exception as e:
        st.error(e)
        return e

def get_files(course_id=None):
    headers = get_headers()
    try:
        if course_id:
            response = requests.get(FILE_API_URL, params={'course_id': course_id}, headers=headers)
        else:
            response = requests.get(FILE_API_URL)

        return process_json(response, "nil", "many")
    
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def upload_files(data, files):
    headers = get_headers()
    try:
        if not data or not isinstance(data, dict):
            raise ValueError("Missing metadata")
        if not files or not isinstance(files, dict):
            raise ValueError("Missing file")

        form_data = {k: str(v) for k, v in data.items()}

        response = requests.post(FILE_API_URL, files=files, data=form_data, headers=headers)
        response.raise_for_status()  # catch 4xx/5xx
        jsend = response.json()

        return process_json(jsend, "Upload Success")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None

def embed_file(_id: str):
    try:
        headers = get_headers()
        response = requests.post(EMBED_API_URL, json={"_id": _id}, headers=headers)
        return process_json(response, "result")
    except Exception as e:
        return e

def delete_files(file_id=None, payload=None):
    headers = get_headers()
    try:
        if file_id:
            response = requests.delete(f"{FILE_API_URL}/{file_id}", headers=headers)
        else:
            response = requests.delete(FILE_API_URL, json={"delete": payload})
        return process_json(response, "Deleted")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def view_file(path):
    headers = get_headers()
    try:
        response = requests.get(f"{FILE_API_URL}/view", params={"path": path}, headers=headers)
        return process_json(response, "nil")
    except Exception as e:
        return None

def get_embeds():
    headers = get_headers()
    try:
        response = requests.get(EMBED_API_URL, headers=headers)
        return process_json(response, "nil")
    except Exception as e:
        return None
    
def get_prompts():
    headers = get_headers()
    try:
        r = requests.get(PRMPT_API_URL, timeout=5, headers=headers)
        r.raise_for_status()
        return r.json()  # always return JSON if no exception
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching prompts: {e}")
        return None

def get_feedbacks():
    headers = get_headers()
    try:
        r = requests.get(FDBK_API_URL, headers=headers)
        return process_json(r, "nil")
    except Exception as e:
        return None
    
def get_categories():
    headers = get_headers()
    try:
        r = requests.get(REQ_API_URL + "/category", headers=headers)
        return process_json(r, "nil")
    except Exception as e:
        return None
    
def add_categories(cat_data):
    headers = get_headers()
    try:
        r = requests.post(REQ_API_URL + "/category", json=cat_data, headers=headers)
        return process_json(r, "Added")
    except Exception as e:
        return None
    
def delete_categories(ids):
    headers = get_headers()
    try:
        r = requests.delete(REQ_API_URL + "/category", json=ids, headers=headers)
        return process_json(r, "Deactivated")
    except Exception as e:
        return None

def get_issues():
    headers = get_headers()
    try:
        r = requests.get(REQ_API_URL + "/issue", headers=headers)
        return process_json(r, "nil")
    except Exception as e:
        return None
    
def add_issues(cat_data):
    headers = get_headers()
    try:
        r = requests.post(REQ_API_URL + "/issue", json=cat_data, headers=headers)
        return process_json(r, "Added")
    except Exception as e:
        return None

def add_feedback(fb_data):
    headers = get_headers()
    try:
        r = requests.post(FDBK_API_URL, json=fb_data, headers=headers)
        return process_json(r, "Added")
    except Exception as e:
        return None

def get_feedback_summary():
    headers = get_headers()
    try:
        r = requests.get(FDBK_API_URL + "/ai", headers=headers)
        return process_json(r, "nil")
    except Exception as e:
        return ""