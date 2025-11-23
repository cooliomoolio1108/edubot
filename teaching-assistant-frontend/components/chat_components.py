import streamlit as st
from utils.chat_functions import save_convo_id
import time
from utils.chat_functions import chat_classroom
from ast import literal_eval
from utils.chat_helpers import stream_message
from bson import ObjectId

def parse_classroom_content(raw):
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    return [literal_eval(line) for line in lines]

persona_emojis = {
    "Wei Ling": "👩🏻‍🎓",   # Overachiever
    "Zara": "👩🏽‍🎨",       # Creative Thinker
    "Jun Wei": "🧑🏻‍💼",     # Quiet Observer
    "Chloe": "👩🏼‍🤝‍👩🏽",   # Social Butterfly
    "Darren": "👨🏻‍💻",      # Tech Whiz
    "Farid": "🧑🏾‍🏫",       # Skeptic / Critical Thinker
    "Bryan": "🧑🏻‍🎤",        # Class Clown / Entertainer
    "Classroom": "🏫",
    "teacher": "👩🏻‍🏫"
}

chat_ans_mode = {
    "Direct": "direct",
    "Socratic": "socratic",
    "Quiz": "quiz",
}
chat_tone = {
    "Normal": "normal",
    "Friendly": "friendly",
    "Strict": "strict",
}
chat_depth ={
    "Normal": "normal",
    "Quick": "shallow",
    "In-Depth": "deep",
}

def format_options(dict, choice, default="keys"):
    if default == "keys":
        return dict.get(choice)
    else:
        for k, v in dict.items():
            if v == choice:
                return k

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
            new_convo_id = save_convo_id(title, course_options[option])
            if new_convo_id:
                st.session_state.conversations.append({
                    "title": title,
                    "messages": [],
                    "title_updated": False,
                    "course_id": course_options[option]
                })
                st.session_s

def sidebar_convo_render():
    with st.sidebar:
        if st.button("New Conversation", type="primary"):
            create_convo()
        st.title("Course Chats")
        courses = st.session_state.get("courses", [])
        course_convos = st.session_state.get("conversations", {})
        st.write(course_convos)
        if courses and course_convos:
            for c in courses:
                with st.expander(f"{c.get('course_name', 'Unnamed Course')}"):
                    for key, value in course_convos.items():
                        if c.get("_id") == value.get("course_id"):
                            title = value.get("title", "No title")
                            if st.button(f"{title}", key=f"convo_{key}"):
                                st.session_state.current_conversation = key

def normal_chat_config(edit_convo,current_convo_data={},convo_id=None):
    with st.sidebar:
        def_temp = current_convo_data.get("temperature", 0.2)
        def_ans_mode = format_options(chat_ans_mode, current_convo_data.get("answer_mode", "direct"), "values")
        def_tone = format_options(chat_tone, current_convo_data.get("response_tone", "normal"), "values")
        def_depth = format_options(chat_depth, current_convo_data.get("response_depth", "normal"), "values")
        def_speed = current_convo_data.get("response_speed", 0.0)
        with st.form("Chat Config"):
            temperature = st.slider("Temperature", 0.0, 1.0, float(def_temp), 0.1, key="temperature", disabled=not convo_id)
            response_speed = st.slider("Response Speed",0.0, 1.0, float(def_speed), 0.1, disabled=not convo_id, help="This is the streaming speed in seconds per character.")
            ans_mode = st.segmented_control("Chat Mode", chat_ans_mode.keys(), key="chat_mode",disabled=not convo_id, default=def_ans_mode, width="stretch")
            response_tone = st.segmented_control("Response Tone", chat_tone.keys(), disabled=not convo_id, default=def_tone, width="stretch")
            response_depth = st.segmented_control("Response Depth",chat_depth.keys(), disabled=not convo_id, default=def_depth, width="stretch")
            st.write("-----")
            submit = st.form_submit_button("Save Configuration",width="stretch", disabled=not convo_id)
            if submit:
                mode_str = format_options(chat_ans_mode,ans_mode)
                resp_tone_str = format_options(chat_tone,response_tone)
                resp_dep_str = format_options(chat_depth,response_depth)
                changes = {
                    "temperature": temperature,
                    "answer_mode": mode_str,
                    "response_speed": response_speed,
                    "response_tone": resp_tone_str,
                    "response_depth": resp_dep_str
                }
                result = edit_convo(convo_id, changes)
                if not result:
                    st.error("Failed to save configuration")
                else:
                    st.rerun()

def classroom_config(convo_id=None):
    with st.sidebar:
        if st.button("Classroom Style Discussion", type="primary", width="stretch", disabled=not convo_id):
            return True

@st.dialog("Classroom Session", width="large")
def classroom_session(send_to_gpt=None):
    if "active_classroom" not in st.session_state:
        st.session_state.active_classroom = []
    classroom_chat = st.session_state.active_classroom

    query = st.chat_input("Enter your query here.")

    if query:
        human_message = {"role": "user", "query": query}
        classroom_chat.append(human_message)
        st.session_state.active_classroom = classroom_chat

    for message in classroom_chat:
        role = message.get("role", "unknown")
        with st.chat_message(role):
            st.write(message.get("query"))

    if query and send_to_gpt:
        with st.chat_message("assistant"):
            response = send_to_gpt(query)
            st.write(response)
            classroom_chat.append({"role": "assistant", "query": response})

def classroom_inline_session(send_message_to_db=None, convo_id=None, course_title=None,classroom_id=None):
    key = f"classroom"

    # 1️⃣ Each classroom keeps its own chat history
    if key not in st.session_state:
        st.session_state[key] = []

    chat = st.session_state[key]
    with st.expander(f"Classroom Session {classroom_id or 'Unknown'}", expanded=True):
        query = st.chat_input("Enter your query for classroom discussion:",
                            key=f"input_{key}")
        
        if query:
            user_msg = {
                "_id": ObjectId(),
                "role": "user",
                "content": query,
                "sources": [],
                "answer_mode": "direct",
                "summary": "",
                "is_classroom": True
            }
            chat.append(user_msg)
            if send_message_to_db:
                send_message_to_db(convo_id, "user", query, True)
            with st.container(border=True):
                with st.spinner("Discussion is starting"):
                    end_class = chat_classroom(convo_id, query, course_title)
                    if end_class:
                        chat.append(end_class)
                        st.session_state.classroom_chat_input = False
                        st.rerun()
            st.session_state[key] = chat

        if not chat:
            st.info("No messages yet. Start the discussion above!")
        else:
            for message in chat:
                st.write("This is message:",message)
                with st.chat_message(message["role"]):
                    content = message.get("content", {})

                    if isinstance(content, dict):
                        # It's a dict with context + question
                        content = query.get("content", "")
                        question = query.get("question", "")
                        if content:
                            st.markdown(f"{content}")
                        if question:
                            st.markdown(f"**Question:** {question}")
                    elif isinstance(query, str):
                        format_classroom(content)
                    else:
                        st.write(str(query))
        if st.button("End Classroom Session", key=f"endclass_{classroom_id}", width="stretch"):
            st.session_state.classroom_chat_input = False
            st.rerun()

def group_messages(convo_data):
    classroom_chats = []
    if isinstance(convo_data, dict) or isinstance(convo_data, list):
        messages = convo_data.get("messages")
        if messages and isinstance(messages, list):
            for m in messages:
                is_classroom = m.get("is_classroom", False)
                if is_classroom:
                    classroom_chats.append(m)
                    messages.remove(m)
    return classroom_chats, messages

def format_classroom(message):
    _id_l4 = str(message.get("_id", "No ID found"))[-4:]
    content = message.get("content", None)
    if not content:
        return "Error"
    with st.chat_message("Classroom", avatar=persona_emojis["Classroom"]):
        st.info("Expand to see the whole classroom discussion")
        with st.expander(f"Classroom #{_id_l4}"):
            list_msg = parse_classroom_content(content)
            for l in list_msg:
                l_dict = dict(l)
                role = l_dict.get("persona", None)
                if not role:
                    return "Error in role parsing"
                with st.chat_message(role, avatar=persona_emojis[role]):
                    stream_message(l_dict.get("content"), "old")

def format_socratic(idx, message):
    content = message.get("content")
    summary = message.get("summary")
    if not content:
        st.error("Error reading message")
        return
    st.warning("💡 This is a hint for you to consider:")
    with st.container(key=f"hint_container_{idx}", border=True):
        if summary:
            st.info(f"Let's look at a small excerpt from the NTULEARN materials!\n\n{summary}")
        else:
            st.write("No summary available")
        stream_message(content, 'old')
        