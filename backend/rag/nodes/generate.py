from rag.graph.state import State
from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer
from dotenv import load_dotenv
from database import prompt_collection
import re
from urllib.parse import quote
from. import llm_stream, PERSONAS

SOURCE_PATTERN = re.compile(
    r"\[\s*source:\s*(?P<fname>[^,\]]+)\s*,\s*pages?:\s*(?P<pages>\d+(?:\s*,\s*\d+)*)\s*\]\s*$",
    re.IGNORECASE,
)

def wrap_source_link(gpt_text: str, base_url: str) -> str:
    """
    Turns trailing `[source: file.pdf, Page(s): ...]` into:
    '...  \n[Source](<base_url>/files/<file.pdf>), Pages: 1, 5, 39'
    """
    m = SOURCE_PATTERN.search(gpt_text.strip())
    print("MATCHYYY", m)
    if not m:
        return gpt_text

    fname = m.group("fname").strip()
    pages = m.group("pages").replace(" ", "")
    url = f"{base_url}/files/{quote(fname)}"

    main = gpt_text[:m.start()].rstrip()
    return f"{main}  \n[Source]({url}), Pages: {', '.join(pages.split(','))}"

def get_prompt(course_id):
    prompts = prompt_collection.find_one(
        {"course_id": course_id}
    )
    return prompts

def build_course_scoped_prompt(doc):
    """
    doc: MongoDB document with keys:
        - system_template
        - human_template
    """
    if not doc:
        return generic_prompt
    return ChatPromptTemplate.from_messages([
        ("system", doc.get("system_template")),
        ("human", doc.get("human_template"))
    ])

load_dotenv()
generic_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a course-scoped assistant. Use the provided CONTEXT and HISTORY to answer. "
     "If the user message is a greeting (e.g., 'hi', 'hello', 'hey'), respond with a short greeting and guide them to ask a query about the course, even if there is no relevant CONTEXT/HISTORY. Do not refuse in this case."
     "If the query cannot be answered from CONTEXT or HISTORY or appears out-of-scope for the course "
     "'{course_title}', respond with: "
     "'This chat is limited to '{course_title}'; I couldn't find enough context to answer.' "
     "Answer concisely and include inline citations like [source]. Do not invent citations."
     "Do not include the words 'CONTEXT', 'HISTORY', or meta-references like 'in the context' or 'based on the context' in your answer."
    ),
    ("human",
     "HISTORY:\n{history}\n\n"
     "CONTEXT:\n{context}\n\n"
     "Query:\n{query}\n\n"
     "Requirements:\n"
     "- Rely strictly on CONTEXT and HISTORY.\n"
     "- Cite sources with [source] where helpful.\n"
     "- If insufficient context, use the refusal message above.\n")
])

def generate(state: State):
    print("Generating final answer...")
    prompt = get_prompt(state['course_id'])
    COURSE_SCOPED_PROMPT = build_course_scoped_prompt(prompt)
    hist_text = "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in state['history'])
    messages = COURSE_SCOPED_PROMPT.invoke({"history": hist_text, "query": state["query"], "context": state['context'], "course_title": state['course_title']})
    print("============================")
    print("Sending to GPT:", messages)
    print("============================")
    response = llm_stream.invoke(messages)
    formatted_answer = wrap_source_link(
        response.content,
        base_url="https://my-backend.com"
    )
    sources = state.get("sources")
    return {"answer": formatted_answer, "sources": state.get("sources", "")}

def generate_classroom(state: State) -> dict:
    custom_writer = get_stream_writer()
    query = state["query"]
    summary = state.get("summary", "")
    course = state.get("course_title", "")
    context = state.get("context", [])
    dialogue = []

    # Build unified context text
    if isinstance(context, list):
        context_text = "\n".join([d.page_content for d in context])
    else:
        context_text = str(context)

    base_context = f"""
Simulate a classroom discussion on the topic below.
Each persona speaks one at a time, in this order:
Teacher → Student 1 → Student 2 → Student 3 → Student 4 → Teacher (wrap-up).

Topic: {query}
Course: {course}

Relevant material:
{summary or context_text}
    """

    # Sequential persona responses
    prev_dialogue = ""
    for p in PERSONAS:
        persona_prompt = f"""
{base_context}

Previous dialogue so far:
{prev_dialogue}

Now speak as the {p['role']} ({p['style']}).
Respond in 2–4 sentences.
        """
        response = llm_stream.invoke(persona_prompt).content.strip()
        custom_writer({"persona": p["role"], "content": response})
        dialogue.append({"persona": p["role"], "content": response})
        prev_dialogue += f"\n{p['role'].title()}: {response}"

    # Teacher final wrap-up
    wrap_prompt = f"""
Summarise the key learning points from the classroom discussion above.
Keep the summary concise (3–5 sentences).
    """
    wrap_response = llm_stream.invoke(wrap_prompt).content.strip()

    return {
        "classroom_dialogue": dialogue,
        "answer": wrap_response,
        "is_classroom": True,
    }

def generate_quiz():
    return