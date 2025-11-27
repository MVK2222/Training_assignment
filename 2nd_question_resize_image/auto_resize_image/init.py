import azure.functions as func
import json
import os
from io import BytesIO
from PIL import Image
from azure.storage.blob import BlobServiceClient

# Use the same storage account as everything
BLOB_CONN_STRING = os.environ["AzureWebJobsStorage"]
BLOB_CONTAINER = os.environ["BLOB_CONTAINER"]
RESIZED_CONTAINER = os.environ["RESIZED_CONTAINER"]

blob_service = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)


def main(msg: func.QueueMessage):
    print("🔥 Queue Trigger Fired")

    job = json.loads(msg.get_body().decode())
    blob_url = job["blobUrl"]
    sizes = job["sizes"]

    filename = blob_url.split("/")[-1]

    src_blob = blob_service.get_blob_client(BLOB_CONTAINER, filename)
    original_bytes = src_blob.download_blob().readall()
    img = Image.open(BytesIO(original_bytes))

    output_urls = []

    for size in sizes:
        temp = img.copy()
        temp.thumbnail((size, size))

        buf = BytesIO()
        temp.save(buf, format=img.format or "PNG")
        buf.seek(0)

        path = f"{size}/{filename}"
        out_blob = blob_service.get_blob_client(RESIZED_CONTAINER, path)
        out_blob.upload_blob(buf.getvalue(), overwrite=True)

        output_urls.append(out_blob.url)

    print("Done:", output_urls)
