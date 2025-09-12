import streamlit as st
from utils.chat_functions import (
    save_convo_id,
    save_message_to_db,
    get_convo_id,
    get_messages,
    send_to_gpt,
    simulate_streaming_from_response,
    feedback_in_chat,
    generate_title,
    delete_conversation,
    source_formatter
)
from utils.admin_functions import get_all_courses, get_course
from utils.styling import inject_custom_css
from dotenv import load_dotenv
from utils.auth import require_login
from components import message_toolbar, sidebar_menu
import time
import re
from utils.debug import debug_session_state

st.set_page_config(page_title="Chat Panel", layout="wide")
inject_custom_css()
require_login()
load_dotenv()
sidebar_menu.authenticated_menu()

def convert_to_latex(text: str) -> str:
    # Convert block equations \[...\] → $$...$$
    text = re.sub(r"\\\[(.+?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    # Convert inline equations \(...\) → $...$
    text = re.sub(r"\\\((.+?)\\\)", r"$\1$", text, flags=re.DOTALL)
    return text

def stream_message(text, mode):
    placeholder = st.empty()
    accumulated = ""
    for chunk in text.split(" "):
        if mode == 'new':
            accumulated += chunk + " "
            placeholder.markdown(convert_to_latex(accumulated), unsafe_allow_html=True)
            time.sleep(0.01)  # simulate streaming
        else:
            accumulated += chunk + " "
            placeholder.markdown(convert_to_latex(accumulated), unsafe_allow_html=True)

if "courses" not in st.session_state:
    try:
        data = get_all_courses()
        st.session_state.courses = data
    except Exception as e:
        st.session_state.courses = []
        st.error(e)
    

@st.dialog("Creating Conversation")
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
        if option and st.button("submit", type="primary"):
            st.session_state.create_new_convo = True
            title = "New Chat"
            user_id = st.session_state['user']['oid'] or 'nil'
            new_convo_id = save_convo_id(title, user_id, course_options[option])
            if new_convo_id:
                st.session_state.conversations[new_convo_id] = {
                    "title": title,
                    "messages": [],
                    "title_updated": False,
                    "course_id": course_options[option]
                }
                st.session_state.current_conversation = new_convo_id
            st.rerun()

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

if "create_new_convo" not in st.session_state:
    st.session_state.create_new_convo = False

# Initialize session state
if "conversations" not in st.session_state:
    try:
        conversations =  get_convo_id()
        st.session_state.conversations = {
            convo["_id"]: {
                "title": convo["title"],
                "messages": None,
                "title_updated": convo["title"] != "New Chat",
                "course_id": convo.get('course_code', '')
            }
            for convo in conversations
        }
    except Exception as e:
        st.session_state.conversations = {}
        st.error(f"Failed to load conversations: {str(e)}")
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = {}

# App Title
if st.session_state.current_conversation is None:
    st.title("Teacher Bot")
    st.subheader("Access all your conversations in the sidebar")

# Sidebar: Manage Conversations
with st.sidebar:
    st.title("Conversations")
    if st.button("New Conversation", type="primary"):
        create_convo()
    for convo_id, convo_data in st.session_state.conversations.items():
        col1, col2 = st.columns([7,1])
        label = convo_data.get("title", "Untitled")
        with col1:
            if st.button(label, key=convo_id, width='stretch'):
                st.session_state.current_conversation = convo_id
                # Force one fetch on next render:
                st.session_state.conversations[convo_id]["messages"] = None
                st.rerun()
        with col2:
            popover = st.popover("")
            deletion = popover.button("Delete", key=f'delete_{convo_id}')
            clearCache = popover.button("Clear Cache", key=f'clearCache_{convo_id}')
            if deletion:
                deletion_result = delete_conversation(convo_id)
                st.rerun()
            if clearCache:
                st.rerun()


# Main Chat Window
if st.session_state.current_conversation:
    convo_id = st.session_state.current_conversation
    # Load message history from backend
    convo_data = st.session_state.conversations[convo_id]
    course_id = convo_data.get('course_id' , '')
    # course = get_course(course_id)

    course_title = convo_data.get('course_name' , '')

    if convo_data["messages"] is None:
        # Fetch once because cache is empty
        messages = get_messages(convo_id)
        st.session_state.conversations[convo_id]["messages"] = messages
    else:
        messages = convo_data["messages"]

    # Display conversation title
    st.write(f"# 🧠 {convo_data.get('title', 'Untitled Conversation')}")

    last_msg_count =0
    # Display message history
    # Inside main chat display loop
    for idx, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            # st.markdown(msg["content"])
            stream_message(msg['content'], 'old')
            if msg.get("sources"):
                sourceslist = msg.get("sources", "")
                paramlist = source_formatter(sourceslist)
                st.session_state.paramlist = paramlist
                # if st.button("sources", key=f'viewfile_{idx}'):
                #     show_files()
            if msg["role"] == 'assistant':
                message_toolbar.render(idx, msg)
        last_msg_count = idx
            # st.markdown(msg.get("sources", ""))

# # Display feedback button only for the last assistant message
# if messages and messages[-1]["role"] == "assistant":
#     if st.button("👍", key=f"thumbs_up_last"):
#         feedback_in_chat(5)
#         st.success("Thank you for your feedback!")


    # Chat input
    prompt = st.chat_input("Say something...")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        # Append user message to session + backend
        user_msg = {"role": "user", "content": prompt}
        st.session_state.conversations[convo_id]["messages"].append(user_msg)
        save_message_to_db(convo_id, "user", prompt)
        
        # TODO: Add GPT response handler here (send to backend, display, and save)
        with st.spinner("Thinking..."):
            response = send_to_gpt(convo_id, prompt, course_id, course_title)
        print(response)
        answer = response.get('answer', '')
        source = response.get('sources', '')
        assistant_msg = {"role": "assistant", "content": answer, "sources": source}
        st.session_state.conversations[convo_id]["messages"].append(assistant_msg)
        with st.chat_message("assistant"):
            stream_message(answer, 'new')
            # paramlist = source_formatter(source)
            # st.session_state.paramlist = paramlist
            # if st.button("sources", key=f'viewfile_{last_msg_count + 1}'):
            #     show_files()

        # if not st.session_state.feedback_given:
        #     if messages and messages[-1]["role"] == "assistant":
        #         if st.button("👍", key=f"thumbs_up_last"):
        #             st.session_state.feedback_given = True
        #             feedback_in_chat(5)
        if (st.session_state.conversations[convo_id]["title"] == "New Chat"
            and len(st.session_state.conversations[convo_id]["messages"]) >= 4
            and not st.session_state.conversations[convo_id].get("title_updated", False)):
                st.write("Changing Titles")
                new_title = generate_title(convo_id)
                if isinstance(new_title, dict):
                    st.session_state.conversations[convo_id]["title"] = new_title.get("title", "")
        st.rerun()
else:
    st.warning("Please start a new conversation or access you past conversations in the sidebar.")

# debug_session_state()