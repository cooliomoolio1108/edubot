from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

_embeddings = None
_vector_store = None

def get_vector_store():
    global _embeddings, _vector_store
    if _vector_store is None:
        _embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.environ["EMBED_ENDPOINT"],
            azure_deployment=os.environ["EMBED_DEPLOY_NAME"],
        )
        _vector_store = Chroma(
            collection_name="teach-bot",
            embedding_function=_embeddings,
            persist_directory="./chroma_langchain_db"
        )
        print(f"{_vector_store} is up and running")
    return _vector_store

