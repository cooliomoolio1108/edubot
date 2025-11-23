import streamlit as st
from utils.chat_functions import (
    save_convo_id,
    save_message_to_db,
    get_convo_id,
    get_messages,
    send_to_gpt,
    generate_title,
    delete_conversation,
    source_formatter,
    edit_convo
)
from utils.admin_functions import get_all_courses
from utils.styling import inject_custom_css
from utils.auth import require_login
from utils.chat_helpers import stream_message, get_course_name
from utils.debug import debug_session_state
from components import message_toolbar, sidebar_menu, chat_components
from dotenv import load_dotenv
import logging
import time

logging.basicConfig(
    filename="chat_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
personas = chat_components.persona_emojis

st.set_page_config(page_title="Chat Panel", layout="wide")
inject_custom_css()
require_login()
load_dotenv()
sidebar_menu.authenticated_menu()

@st.dialog("Creating Conversation", width="medium")
def create_convo():
    options = st.session_state.courses
    if options and isinstance(options, (list, set, tuple)):
        course_options = {
            f"{option['course_name']}": option['_id']  # Display title, store code
            for option in options
        }
        option = st.selectbox(
            "Choose a course for this conversation",
            course_options.keys(),
        )
        if option and st.button("Submit", type="secondary", width="stretch"):
            st.session_state.create_new_convo = True
            title = "New Chat"
            new_convo_id = save_convo_id(title, course_options[option])
            if new_convo_id:
                st.session_state.conversations[new_convo_id] = {
                    "title": title,
                    "messages": [],
                    "title_updated": False,
                    "course_id": course_options[option],
                }
                st.session_state.current_conversation = new_convo_id
            st.rerun()

def initiate_ss():
    if "courses" not in st.session_state:
        try:
            data = get_all_courses()
            st.session_state.courses = data
        except Exception as e:
            st.session_state.courses = []
            st.error(e)

    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False

    if "create_new_convo" not in st.session_state:
        st.session_state.create_new_convo = False

    if "convo_error" not in st.session_state:
        st.session_state.convo_error = {"bool": False, "reason": ""}

    # Initialize session state
    if "conversations" not in st.session_state:
        try:
            conversations =  get_convo_id()
            courses = st.session_state.get("courses", [])
            # st.session_state.conversations = conversations
            st.session_state.conversations = {
                convo["_id"]: {
                    "_id": convo["_id"],
                    "classroom": convo.get("classroom", ""),
                    "title": convo["title"],
                    "messages": None,
                    "title_updated": convo["title"] != "New Chat",
                    "course_id": convo.get('course_id', ''),
                    "course_name": get_course_name(convo.get('course_id', ''), courses),
                    "answer_mode": convo.get('answer_mode'),
                    "temperature": convo.get('temperature', 0.2),
                    "response_tone": convo.get('response_tone', 'normal'),
                    "response_depth": convo.get('response_depth', 'normal'),
                    "response_speed": convo.get('response_speed', 0.0),
                }
                for convo in conversations
            }
        except Exception as e:
            st.session_state.conversations = {}
            st.error(f"Failed to load conversations: {str(e)}")

    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = None
    
    if "classroom_chat_input" not in st.session_state:
        st.session_state.classroom_chat_input = False

initiate_ss()
current_convo = st.session_state.get("current_conversation", None)
st.sidebar.title("Chat Configuration")
st.sidebar.info("Click below to start a multi-persona classroom style chat!", icon="ℹ️")
if chat_components.classroom_config(current_convo):
    st.session_state.classroom_chat_input = True
if current_convo:
    current_convo_data = st.session_state.conversations.get(current_convo, {})
    chat_components.normal_chat_config(edit_convo, current_convo_data, current_convo)
clr_flag = st.session_state.classroom_chat_input

with st.sidebar:
    st.title("Course Chats")
    if st.button("New Conversation", type="primary"):
        create_convo()
    courses = st.session_state.get("courses", [])
    course_convos = st.session_state.get("conversations", {})
    if courses and course_convos:
        for c in courses:
            with st.expander(f"{c.get('course_name', 'Unnamed Course')}"):
                for key, value in course_convos.items():
                    if c.get("_id") == value.get("course_id"):
                        title = value.get("title", "No title")
                        if st.button(f"{title}", key=f"convo_{key}"):
                            st.session_state.current_conversation = key
                            st.rerun()

# Main Chat Window
if st.session_state.current_conversation:
    course_id = current_convo_data.get('course_id' , '')
    course_title = current_convo_data.get('course_name' , '')
    if current_convo_data["messages"] is None:
        # Fetch once because cache is empty
        messages = get_messages(current_convo)
        st.session_state.conversations[current_convo]["messages"] = messages
    else:
        messages = current_convo_data["messages"]

    # Display conversation title
    st.write(f"# 🧠 {current_convo_data.get('title', 'Untitled Conversation')}")
    # classroom_msgs, normal_msgs = chat_components.group_messages(current_convo_data)
    last_msg_count =0
    for idx, msg in enumerate(messages):
        role = msg.get("role", "assistant").capitalize()
        role_emoji = personas.get(msg.get("role", ""))
        if msg.get("is_classroom") and msg.get("role")=="assistant":
            chat_components.format_classroom(msg)
        else:
            with st.chat_message(msg["role"], avatar=role_emoji, width="stretch"):
                if msg.get("role") not in ("user", "assistant"):
                    st.info(f"{role}")
                if msg.get("sources"):
                    sourceslist = msg.get("sources", "")
                    paramlist = source_formatter(sourceslist)
                    st.session_state.paramlist = paramlist
                if msg.get("answer_mode", "") == "socratic":
                    chat_components.format_socratic(idx, msg)
                else:
                    stream_message(msg["content"], 'old')
                if msg["role"] == 'assistant':
                    message_toolbar.render(idx, msg, current_convo)
        last_msg_count = idx
            # st.markdown(msg.get("sources", ""))

    error = st.session_state.convo_error
    if error.get("bool", ""):
        st.error(error.get("reason"))
        st.session_state.convo_error = {"bool": False, "reason": ""}

    # Chat input
    prompt = st.chat_input("Say something...", disabled=st.session_state.classroom_chat_input)
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        # Append user message to session + backend
        user_msg = {"role": "user", "content": prompt}
        st.session_state.conversations[current_convo]["messages"].append(user_msg)
        save_message_to_db(current_convo, "user", prompt)
        
        # TODO: Add GPT response handler here (send to backend, display, and save)
        with st.spinner("Thinking..."):
            response = send_to_gpt(current_convo, prompt, course_title)
        if isinstance(response, dict):
            print(response)
            content = response.get('content', '')
            if not content:
                content = response.get('hint', "I'm sorry, I couldn't generate a response.")
            answer_mode = response.get('answer_mode', '')
            source = response.get('sources', '')
            inserted_id = response.get('inserted_id', '')
            summary = response.get('summary', '')
            assistant_msg = {"role": "assistant", "content": content, "sources": source, "answer_mode": answer_mode, "summary": summary}
            st.session_state.conversations[current_convo]["messages"].append(assistant_msg)
            with st.chat_message("assistant"):
                if answer_mode == 'socratic':
                    chat_components.format_socratic(inserted_id, response)
                else:
                    stream_message(content, 'new')

        else:
            content = str(response)
            st.session_state.convo_error = {"bool": True, "reason": content}
        
        if (st.session_state.conversations[current_convo]["title"] == "New Chat"
            and len(st.session_state.conversations[current_convo]["messages"]) >= 4
            and not st.session_state.conversations[current_convo].get("title_updated", False)):
                new_title = generate_title(current_convo)
                if isinstance(new_title, dict):
                    st.session_state.conversations[current_convo]["title"] = new_title.get("title", "")
        st.rerun()
else:
    st.warning("Please start a new conversation or access you past conversations in the sidebar.")

if clr_flag:
    chat_components.classroom_inline_session(save_message_to_db, current_convo, course_title)
# debug_session_state()