import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from app.core.settings import get_settings

settings  = get_settings()

cache_dir = Path("./.cache/models")
cache_dir.mkdir(parents=True, exist_ok=True)

blob_name = settings.azure_storage_endpoint_cl_blob_name
 

def download_model_from_blob():

    local_model_path = cache_dir / blob_name.split("/")[-1]
    if local_model_path.exists():
        return local_model_path

    blob_service_client = BlobServiceClient(settings.azure_storage_endpoint_cargologik)
    container_client = blob_service_client.get_container_client(settings.azure_storage_endpoint_cl_container_models)
    blob_client = container_client.get_blob_client(blob=blob_name)

    print("Downloading model from Azure Blob Storage...")
    with open(local_model_path, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print("Model downloaded to", local_model_path)
    return local_model_path
