from database import file_collection
from chroma import get_vector_store
from utils.chunkers import PDFChunker
from datetime import datetime
from bson import ObjectId

vector_store = get_vector_store()

def embed_pdf_bytes(pdf_bytes, file_doc):
    chunker = PDFChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_pdf(pdf_bytes, file_doc)
    print("ITWORS", file_doc)
    doc_ids = vector_store.add_documents(chunks)
    _id = file_doc.get('_id')
    print("ITWORS")
    result = file_collection.update_one(
        {"_id": ObjectId(_id)},
        {"$set": {"embedded": True, "doc_ids": doc_ids}}
    )
    print(result)

    return {"status": "embedded", "count": len(doc_ids)}

