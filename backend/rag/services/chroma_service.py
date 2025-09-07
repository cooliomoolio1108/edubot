import chromadb
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["EMBED_ENDPOINT"],
    azure_deployment=os.environ["EMBED_DEPLOY_NAME"],
)

vector_store = Chroma(
    collection_name="teach-bot",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db"
)
print(f'{vector_store} is up and running')
