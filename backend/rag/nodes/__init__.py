from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
from chroma import get_vector_store, get_embeddings

load_dotenv()
vector_store = get_vector_store()
embed_model = get_embeddings()

llm_stream = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZ_OPENAI_ENDPOINT"),
    openai_api_version="2024-12-01-preview",
    model_name = "gpt-4o",
    openai_api_key=os.getenv("AZ_OPENAI_API_KEY"),
    openai_api_type="azure",
    temperature=0.3,
    streaming=False,
)

RELEVANCE_THRESHOLD = 1.52
PERSONAS = [
    {
        "role": "teacher",
        "style": "Encouraging and guiding; clarifies misconceptions and connects ideas.",
    },
    {
        "role": "Wei Ling",
        "style": "Curious and analytical; asks deep 'why' and 'how' questions.",
    },
    {
        "role": "Zara",
        "style": "Creative thinker; uses analogies or visual explanations.",
    },
    {
        "role": "Farid",
        "style": "Skeptical and detail-oriented; challenges assumptions or errors.",
    },
    {
        "role": "Jun Wei",
        "style": "Reflective summariser; restates and synthesises what others said.",
    },
]
