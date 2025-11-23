import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time
from .auth import create_jwt
from .admin_functions import process_json
from utils.api_client import header, get_headers
import logging
import json
from .chat_helpers import stream_message
from bson.objectid import ObjectId
logging.basicConfig(
    filename="chat_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
MSG_API_URL = os.getenv("FLASK_API_URL") + "/message"
CONVO_API_URL = os.getenv("FLASK_API_URL") + "/conversation"
GPT_API_URL = os.getenv("FLASK_API_URL") + "/chat"
FDBK_API_URL = os.getenv("FLASK_API_URL") + "/feedback"
TITLE_API_URL = os.getenv("FLASK_API_URL") + "/generate_title"

def save_message_to_db(conversation_id, role, prompt, is_classroom=False):
    headers = get_headers()
    payload = {
        "conversation_id": conversation_id,
        "role": role,
        "content": prompt,
        "is_classroom": is_classroom
    }
    response = requests.post(MSG_API_URL, json=payload, headers=headers)
    response.raise_for_status()  # optional: raise if not 2xx
    return response


def save_convo_id(title, course_id):
    try:
        headers = get_headers()
        payload = {"title": title, "course_id":course_id}
        res = requests.post(CONVO_API_URL, json=payload, headers=headers)
        return process_json(res, "Convo Created")
    except Exception as e:
        return None

def get_convo_id():
    headers = get_headers()
    response = requests.get(CONVO_API_URL, headers=headers)

    if response.status_code == 200:
        return response.json()  # This will be a list of conversation dicts
    else:
        print("Failed to fetch conversations:", response.text)
        return []
    

def send_to_gpt(convo_id, query, course_title, is_classroom=False) -> str:
    headers = get_headers()
    try:
        response = requests.post(GPT_API_URL, json={
            "convo_id": convo_id,
            "query": query,
            "course_title": course_title,
            "is_classroom": is_classroom
        }, headers=headers)
        response.raise_for_status()
        resp_json = response.json()
        logging.info(
            f"QUERY: {query} | RESPONSE: {response.json()}"
        )
        return resp_json
    except requests.RequestException as e:
        return process_json(e.response, "Failed")


def get_messages(convo_id):
    headers = get_headers()
    getUrl = MSG_API_URL + f'/{convo_id}'
    response = requests.get(getUrl, headers=headers)

    if response.status_code == 200:
        return response.json()  # This will be a list of conversation dicts
    else:
        print("Failed to fetch conversations:", response.text)
        return []

def simulate_streaming_from_response(title: str, full_response: str):
    # Simulate streaming word-by-word
    if title == 'title':
        for word in full_response.split(" "):
            yield word + " "
            time.sleep(0.1)  # Adjust for desired speed
    else:
        for word in full_response.split(" "):
            yield word + " "
            time.sleep(0.02)  # Adjust for desired speed
        

def feedback_in_chat(number):
    feedback = {
        "stars": number,
        "comment": "5 Stars for in chat 'Thumbs Up'"
    }
    print("Sending to:", FDBK_API_URL)
    try:
        response = requests.post(FDBK_API_URL, json=feedback)
        response.raise_for_status()
        print("✅ Feedback submitted:", response.json())
    except Exception as e:
        st.error(f"❌ Failed to send feedback: {e}")

def generate_title(convo_id):
    headers = get_headers()
    try:
        response = requests.post(TITLE_API_URL, json={
            "conversation_id":convo_id
        }, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Failed to send information to generate title: {e}")

def delete_conversation(convo_id):
    headers = get_headers()
    deletion_url = CONVO_API_URL + f'/{convo_id}'
    try:
        response = requests.delete(deletion_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f'❌')

def source_formatter(sourcelist):
    tokens = []
    for d in sourcelist or []:
        if "source" in d and "page" in d:
            tokens.append(create_jwt({"source": d["source"], "page": d["page"]}))
    return tokens

def edit_convo(convo_id, changes: dict):
    headers = get_headers()
    edit_url = CONVO_API_URL + f'/{convo_id}'
    try:
        response = requests.put(edit_url, json=changes, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f'❌ Failed to edit conversation: {e}')
        return None
    
def chat_classroom(convo_id, query, course_title):
    container = st.empty()
    text_log = ""
    text_log_v = ""
    headers = get_headers()
    try:
        with requests.post(
            "http://localhost:5050/chat/classroom",
            json={"query": query, "convo_id": convo_id, "course_title": course_title, "is_classroom": True},
            stream=True,
            headers=headers
        ) as r:
            for line in r.iter_lines():
                if not line:
                    continue

                if line.startswith(b"data: "):
                    data = line.decode()[6:]
                    if data == "[END]":
                        st.success("✅ Classroom simulation complete")
                        break

                    chunk = json.loads(data)
                    text_log += str(chunk)
                    # Each chunk is {"persona": "...", "content": "..."}
                    persona = chunk.get("persona", "assistant")
                    content = chunk.get("content", "")

                    # Display persona dialogue immediately
                    with st.chat_message(persona):
                        stream_message(content, "new")
                        with st.spinner("Next student"):
                            time.sleep(2)
            temp_msg = {
                "_id": ObjectId(),
                "role": "Classroom",
                "content": text_log,
                "sources": [],
                "answer_mode": "direct",
                "summary": "",
                "is_classroom": True
            }

            return temp_msg
    except Exception as e:
        st.error(f"Streaming error: {e}")
        print("Streaming error:", e)