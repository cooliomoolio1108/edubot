from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings  # or any

def embed_file(file_doc):
    loader = PyMuPDFLoader(file_doc["path"])
    docs = loader.load()  # list of Documents

def embed_chunks(docs, file_id):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embedding_model = OpenAIEmbeddings()

    # Add file_id as metadata to each chunk
    for chunk in chunks:
        chunk.metadata["file_id"] = file_id

    vectorstore.add_documents(chunks)
    return [chunk.metadata['id'] for chunk in chunks]  # assuming you assign or get IDs