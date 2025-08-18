
import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient

cache_dir = Path('./.cache/models')
cache_dir.mkdir(parents=True, exist_ok=True)

blob_name = 'llama-prompt-guard-onnx/model.onnx'
azure_conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')

if not azure_conn_str:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set.")

client = BlobServiceClient.from_connection_string(azure_conn_str).get_blob_client('models', blob_name)

with open(cache_dir / blob_name.split('/')[-1], 'wb') as f:
    f.write(client.download_blob().readall())
