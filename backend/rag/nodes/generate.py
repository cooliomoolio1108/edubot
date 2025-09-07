from rag.graph.state import State
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
from ..services.mongodb_service import prompt_collection
import re
from urllib.parse import quote

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
    return ChatPromptTemplate.from_messages([
        ("system", doc["system_template"]),
        ("human", doc["human_template"])
    ])

load_dotenv()
# COURSE_SCOPED_PROMPT = ChatPromptTemplate.from_messages([
#     ("system",
#      "You are a course-scoped assistant. Use the provided CONTEXT and HISTORY to answer. "
#      "If the user message is a greeting (e.g., 'hi', 'hello', 'hey'), respond with a short greeting and guide them to ask a question about the course, even if there is no relevant CONTEXT/HISTORY. Do not refuse in this case."
#      "If the question cannot be answered from CONTEXT or HISTORY or appears out-of-scope for the course "
#      "'{course_title}', respond with: "
#      "'This chat is limited to '{course_title}'; I couldn't find enough context to answer.' "
#      "Answer concisely and include inline citations like [source]. Do not invent citations."
#      "Do not include the words 'CONTEXT', 'HISTORY', or meta-references like 'in the context' or 'based on the context' in your answer."
#     ),
#     ("human",
#      "HISTORY:\n{history}\n\n"
#      "CONTEXT:\n{context}\n\n"
#      "QUESTION:\n{question}\n\n"
#      "Requirements:\n"
#      "- Rely strictly on CONTEXT and HISTORY.\n"
#      "- Cite sources with [source] where helpful.\n"
#      "- If insufficient context, use the refusal message above.\n")
# ])

llm_stream = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZ_OPENAI_ENDPOINT"),
    openai_api_version="2024-12-01-preview",
    model_name = "gpt-4o",
    openai_api_key=os.getenv("AZ_OPENAI_API_KEY"),
    openai_api_type="azure",
    temperature=0.3,
    streaming=False,
)

def generate(state: State):
    prompt = get_prompt(state['course_id'])
    COURSE_SCOPED_PROMPT = build_course_scoped_prompt(prompt)
    hist_text = "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in state['history'])
    messages = COURSE_SCOPED_PROMPT.invoke({"history": hist_text, "question": state["question"], "context": state['context'], "course_title": state['course_title']})
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