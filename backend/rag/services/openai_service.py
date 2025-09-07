from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

llm_stream = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZ_OPENAI_ENDPOINT"),
    openai_api_version="2024-12-01-preview",
    model_name = "gpt-4o",
    openai_api_key=os.getenv("AZ_OPENAI_API_KEY"),
    openai_api_type="azure",
    temperature=0.3,
    streaming=False,
)

def format_messages(messages: list[dict]):
    formatted = []
    for m in messages:
        if m["role"] == "user":
            formatted.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            formatted.append(AIMessage(content=m["content"]))
    return formatted

def get_openai_response(messages: list[dict]) -> str:
    formatted_messages = format_messages(messages)

    # Use streaming correctly
    response = llm_stream.invoke(formatted_messages)
    return response.content

def generate_title_for_chat(messages: list[dict]) -> str:
    formatted_messages = format_messages(messages)
    system_prompt = (
        "Summarize the conversation in 3-5 words."
        "Be more generic with yout titles"
        "Make sure the Title is properly capitalise for first alphabet"
        "Output only the title text. Do not include quotation marks, punctuation, or additional commentary."
        "Ignore messages like hello, hi and other introductory phrases"
    )
    final = [SystemMessage(content=system_prompt)] + formatted_messages
    response = llm_stream.invoke(final)
    print("The title is: ", response.content.strip())
    return response.content.strip()