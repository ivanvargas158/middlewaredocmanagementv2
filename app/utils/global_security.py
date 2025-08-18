import os
import asyncio
from pathlib import Path
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from azure.storage.blob import BlobServiceClient
from app.core.settings import get_settings

settings  = get_settings()

class InjectionGuardModel:
    _instance = None          # Singleton instance
    _lock = asyncio.Lock()    # Async lock for safe initialization

    def __new__(cls):
        # Ensure singleton identity
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init(self):
        """Async initializer (call once at app startup)."""
        async with self._lock:
            if hasattr(self, "session"):  # Already initialized
                return self         

            # === Cache Directory ===
            CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", "./.cache/models"))
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            LOCAL_MODEL_PATH = CACHE_DIR / "model.onnx"

            # === Download if not cached ===
            if not LOCAL_MODEL_PATH.exists():
                blob_service_client = BlobServiceClient(settings.azure_storage_endpoint_cargologik)
                container_client = blob_service_client.get_container_client(settings.azure_storage_endpoint_cl_container_models)
                blob_client = container_client.get_blob_client(blob=settings.azure_storage_endpoint_cl_blob_name)
                with open(LOCAL_MODEL_PATH, "wb") as f:
                    f.write(blob_client.download_blob().readall())

            # === Load tokenizer + ONNX session ===
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            self.session = ort.InferenceSession(str(LOCAL_MODEL_PATH), providers=["CPUExecutionProvider"])
            print("InjectionGuardModel initialized")

        return self

    def _to_numpy(self, tensor):
        if isinstance(tensor, ort.OrtValue):
            return tensor.numpy()
        elif hasattr(tensor, "to_dense"):
            return tensor.to_dense().numpy()
        elif isinstance(tensor, np.ndarray):
            return tensor
        else:
            return np.array(tensor)

    def predict(self, text, threshold=0.5):
        encoded = self.tokenizer(
            text, return_tensors="np", padding=True, truncation=True, max_length=256
        )

        ort_inputs = {
            k: v for k, v in encoded.items()
            if k in [i.name for i in self.session.get_inputs()]
        }

        outputs = self.session.run(None, ort_inputs)
        dense_outputs = [self._to_numpy(o) for o in outputs]

        logits = dense_outputs[0][0]
        prob_malicious = 1 / (1 + np.exp(-logits[1]))
        is_malicious = prob_malicious > threshold

        return {
            "score": float(prob_malicious),
            "is_malicious": bool(is_malicious),
        }
