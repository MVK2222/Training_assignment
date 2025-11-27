import azure.functions as func
import os
import json
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient
from requests_toolbelt.multipart import decoder

ALLOWED = {".png", ".jpg", ".jpeg"}

def is_image(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED

# Use same storage account for everything
BLOB_CONN_STRING = os.environ["AzureWebJobsStorage"]
BLOB_CONTAINER = os.environ["BLOB_CONTAINER"]
QUEUE_NAME = os.environ["QUEUE_NAME"]

def enqueue_resize_message(blob_url: str):
    queue = QueueClient.from_connection_string(BLOB_CONN_STRING, QUEUE_NAME)
    try:
        queue.create_queue()
    except:
        pass

    message = {
        "blobUrl": blob_url,
        "sizes": [320, 1024]
    }

    queue.send_message(json.dumps(message))


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        blob_service = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)
        container = blob_service.get_container_client(BLOB_CONTAINER)

        try:
            container.create_container()
        except:
            pass

        content_type = req.headers.get('Content-Type', '')

        if "multipart/form-data" in content_type:
            body = req.get_body()
            multipart_data = decoder.MultipartDecoder(body, content_type)

            filename = None
            file_data = None

            for part in multipart_data.parts:
                disp = part.headers.get(b"Content-Disposition", b"").decode()
                if "filename=" in disp:
                    filename = disp.split("filename=")[1].strip().replace('"', "")
                    file_data = part.content
                    break

            if not filename or not file_data:
                return func.HttpResponse("No file found", status_code=400)

            if not is_image(filename):
                return func.HttpResponse("Only images allowed", status_code=400)

            blob = container.get_blob_client(filename)
            blob.upload_blob(file_data, overwrite=True)

            blob_url = blob.url

            enqueue_resize_message(blob_url)

            return func.HttpResponse(f"Uploaded {filename}\nQueue added", status_code=200)

        return func.HttpResponse("Expected multipart/form-data", status_code=400)

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
