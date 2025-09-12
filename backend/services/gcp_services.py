from flask import request
import fitz
from storage import bucket
from datetime import datetime

def view_file():
    blob_name = request.args.get("path")
    url = generate_signed_url(blob_name, expiration_minutes=30)
    return {"url": url}

def generate_signed_url(blob_name, expiration_minutes=60):
    blob = bucket.blob(blob_name)
    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=expiration_minutes),
        method="GET"
    )

def upload_file_to_gcp(file_obj, destination_name):
    blob = bucket.blob(destination_name)
    
    # If file_obj is Flask's FileStorage (direct stream)
    blob.upload_from_file(file_obj, rewind=True)
    
    return blob.public_url

def open_pdf_from_gcp_stream(blob_name):
    blob = bucket.blob(blob_name)

    pdf_bytes = blob.download_as_bytes()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return doc