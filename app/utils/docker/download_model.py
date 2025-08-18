from pathlib import Path
from azure.storage.blob import BlobServiceClient
from app.core.settings import get_settings

settings = get_settings()

cache_dir = Path("./.cache/models/llama-prompt-guard-onnx")
cache_dir.mkdir(parents=True, exist_ok=True)

blob_prefix = "llama-prompt-guard-onnx/"  # folder prefix in Azure container


def download_model_from_blob():
    blob_service_client = BlobServiceClient(settings.azure_storage_endpoint_cargologik)
    container_client = blob_service_client.get_container_client(
        settings.azure_storage_endpoint_cl_container_models
    )

    # List all blobs under prefix
    blob_list = container_client.list_blobs(name_starts_with=blob_prefix)

    local_files = []
    for blob in blob_list:
        blob_name = blob.name
        file_name = blob_name.split("/")[-1]
        local_path = cache_dir / file_name

        if not local_path.exists():
            print(f"Downloading {blob_name} -> {local_path}")
            with open(local_path, "wb") as f:
                f.write(container_client.download_blob(blob_name).readall())
        else:
            print(f"Already exists: {local_path}")

        local_files.append(local_path)

    print("All model files downloaded.")
    return cache_dir
