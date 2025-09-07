import streamlit as st
import threading
import requests
import os
from dotenv import load_dotenv
import time
from datetime import datetime
from bson import ObjectId
from .auth import create_jwt

load_dotenv()
MSG_API_URL = os.getenv("FLASK_API_URL") + "/message"
CONVO_API_URL = os.getenv("FLASK_API_URL") + "/conversation"
GPT_API_URL = os.getenv("FLASK_API_URL") + "/chat"
FDBK_API_URL = os.getenv("FLASK_API_URL") + "/feedback"
TITLE_API_URL = os.getenv("FLASK_API_URL") + "/generate_title"

def save_message_to_db(conversation_id, role, prompt):
    payload = {
        "conversation_id": conversation_id,
        "role": role,
        "content": prompt,
    }
    response = requests.post(MSG_API_URL, json=payload)
    response.raise_for_status()  # optional: raise if not 2xx
    return response


def save_convo_id(title, user_id, course_code):
    payload = {"title": title, "user_id": user_id, "title_updated": False, "course_code":course_code}
    res = requests.post(CONVO_API_URL, json=payload)
    
    if res.status_code == 201:
        json_data = res.json()
        print(json_data)
        return json_data.get("conversation_id")  # Safely returns None if key doesn't exist
    else:
        print("Error creating conversation:", res.text)
        return None

def get_convo_id():
    response = requests.get(CONVO_API_URL)

    if response.status_code == 200:
        return response.json()  # This will be a list of conversation dicts
    else:
        print("Failed to fetch conversations:", response.text)
        return []
    

def send_to_gpt(conversation_id, prompt, course_id, course_title) -> str:
    try:
        response = requests.post(GPT_API_URL, json={
            "conversation_id": conversation_id,
            "prompt": prompt,
            "course_id": course_id,
            "course_title": course_title
        })
        response.raise_for_status()
        resp_json = response.json()
        return resp_json
    except requests.RequestException as e:
        return f"❌ Error contacting backend: {str(e)}"


def get_messages(convo_id):
    getUrl = MSG_API_URL + f'/{convo_id}'
    response = requests.get(getUrl)

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
    try:
        response = requests.post(TITLE_API_URL, json={
            "conversation_id":convo_id
        })
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Failed to send information to generate title: {e}")

def delete_conversation(convo_id):
    deletion_url = CONVO_API_URL + f'/{convo_id}'
    try:
        response = requests.delete(deletion_url)
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