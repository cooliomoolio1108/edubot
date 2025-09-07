import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("EMBED_API_KEY"),  # Load API key from .env
    api_version="2023-05-15",  # API version (check Azure portal for the latest)
    azure_endpoint=os.getenv("EMBED_ENDPOINT")  # Load endpoint from .env
)

def generate_embeddings(texts, deployment_name):
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            input=text,
            model=deployment_name  # Use the deployment name for the embedding model
        )
        embedding = response.data[0].embedding  # Extract the embedding vector
        embeddings.append(embedding)
    return embeddings