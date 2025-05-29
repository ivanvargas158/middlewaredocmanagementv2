from azure.storage.blob import BlobServiceClient
from app.core.settings import get_settings

settings  = get_settings()

def save_file_blob_storagev1(file_bytes:bytes,filename:str,container:str,tenant_name:str,folder_file_name:str)->str:
    blob_service_client = BlobServiceClient(settings.azure_storage_endpoint_cargologik)
    container_client = blob_service_client.get_container_client(container)
    blob_client = container_client.get_blob_client(blob=filename)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_client.url
  
def save_file_blob_storage(file_bytes: bytes, container: str, blob_path:str,account_url:str) -> str:
 
    # Initialize clients
    blob_service_client = BlobServiceClient(account_url)
    container_client = blob_service_client.get_container_client(container)
    blob_client = container_client.get_blob_client(blob=blob_path)

    # Upload the file
    blob_client.upload_blob(file_bytes, overwrite=True)

    return blob_client.url