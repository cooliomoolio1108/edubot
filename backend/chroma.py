from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

_embeddings = None
_vector_store = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.environ["EMBED_ENDPOINT"],
            azure_deployment=os.environ["EMBED_DEPLOY_NAME"],
            api_version="2024-05-01-preview",
        )
    return _embeddings

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        _vector_store = Chroma(
            collection_name="teach-bot",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db",
        )
        print("✅ Chroma vector store initialized.")
    return _vector_store
