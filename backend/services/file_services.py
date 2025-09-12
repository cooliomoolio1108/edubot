from database import file_collection
from datetime import datetime
from . import serialize_id, clean_data
from models.file import File
import os
from bson import ObjectId
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chroma import get_vector_store
from .gcp_services import view_file

vector_store = get_vector_store()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "backend", "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

def find_files():
    files = file_collection.find()
    return [serialize_id(f) for f in files]

def find_files_by_course(course_id: str):
    results = list(file_collection.find({"course_id": course_id}))
    cleaned = [serialize_id(file) for file in results]
    return cleaned

def find_file_by_id(id):
    file_doc = file_collection.find_one({"_id": ObjectId(id)})
    return serialize_id(file_doc)

def find_file_by_file_id(file_id):
    file_doc = file_collection.find_one({"file_id": file_id})
    return serialize_id(file_doc)

def save_files_to_db(data):
    def process(doc):
        return File(**doc).dict(by_alias=True, exclude_none=True)

    if isinstance(data, dict):
        # Single document
        cleaned = process(data)
        result = file_collection.insert_one(cleaned)
        return {"inserted_id": str(result.inserted_id)}

    elif isinstance(data, list):
        # Multiple documents
        cleaned_list = [process(doc) for doc in data if isinstance(doc, dict)]
        if not cleaned_list:
            raise ValueError("No valid documents to insert.")
        result = file_collection.insert_many(cleaned_list)
        return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

    else:
        raise ValueError("Expected a dictionary or a list of dictionaries.")
    
def embed_single_file(file_doc):
    if not file_doc:
        return {"status": "Not Embedded", "reason": "Missing file document"}

    file_path = file_doc["path"]
    file_id = str(file_doc["_id"])
    loader = PyMuPDFLoader(file_path)
    raw_documents = loader.load()

    if not raw_documents or all(doc.page_content.strip() == "" for doc in raw_documents):
        return {"status": "Not Embedded", "reason": "Empty or unreadable content"}

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(raw_documents)

    if not chunks:
        return {"status": "Not Embedded", "reason": "No chunks detected"}

    for chunk in chunks:
        chunk.metadata["file_id"] = file_id
        chunk.metadata["file_name"] = file_doc["file_name"]
        chunk.metadata["course_id"] = file_doc["course_id"]

    doc_ids = vector_store.add_documents(chunks)
    file_collection.update_one(
        {"_id": ObjectId(file_doc["_id"])},
        {
            "$set": {
                "embedded": True,
                "embedding_at": datetime.utcnow(),
                "doc_ids": doc_ids
            }
        }
    )

    print("The collection is length:", vector_store._collection.count())
    return {"status": "embedded", "doc_count": len(doc_ids)}

def delete_embed(file_id):
    filtering = {"file_id": file_id}
    results = vector_store.get(where=filtering)
    ids_to_delete = results["ids"]
    if ids_to_delete:
        vector_store.delete(ids=ids_to_delete)
    return len(ids_to_delete)

def find_embed_by_course(course_id):
    return

def find_embeds():
    chroma_collection = vector_store._collection
    all_data = chroma_collection.get(include=['documents', 'embeddings', 'metadatas'])
    print(all_data)
    return all_data

def delete_file_by_id(id):
    delete_result = file_collection.delete_one({"_id": ObjectId(id)})
    return delete_result.deleted_count
