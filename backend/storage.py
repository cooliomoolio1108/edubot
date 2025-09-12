import os, datetime
from google.cloud import storage

BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
client = storage.Client()  # created once
bucket = client.bucket(BUCKET_NAME)

