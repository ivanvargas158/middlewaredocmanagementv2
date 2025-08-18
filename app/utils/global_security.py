from pathlib import Path
from transformers import AutoTokenizer
import onnxruntime as ort
import numpy as np

class InjectionGuardModel:
    _instance = None

    def __new__(cls, model_dir="app/models/llama-prompt-guard-onnx"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model(model_dir)
        return cls._instance

    def _init_model(self, model_dir):
        model_dir = Path(model_dir).resolve()  # resolves to Linux-style path on App Service

        # Load tokenizer offline
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            local_files_only=True
        )

        # Load ONNX model
        self.session = ort.InferenceSession(
            str(model_dir / "model.onnx"),
            providers=["CPUExecutionProvider"]
        )

            # Store input/output names for ONNX
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

    def predict(self, text, threshold=0.5):
            # Tokenize input
            encoded = self.tokenizer(
                text,
                return_tensors="np",
                padding=True,
                truncation=True,
                max_length=256
            )

            # Match ONNX expected input names
            ort_inputs = {k: v for k, v in encoded.items() if k in self.input_names}

            # Run ONNX model
            outputs = self.session.run(None, ort_inputs)
            dense_outputs = [self._to_numpy(o) for o in outputs]

            # Assuming binary classification: index 1 = "malicious"
            logits = dense_outputs[0][0]
            prob_malicious = 1 / (1 + np.exp(-logits[1]))
            is_malicious = prob_malicious > threshold

            return {
                "text": text,
                "score": float(prob_malicious),
                "is_malicious": bool(is_malicious)
            }


    def _to_numpy(self, tensor):
        """Convert SparseTensor or ndarray to NumPy array."""
        if isinstance(tensor, ort.OrtValue):
            return tensor.numpy()  
        elif isinstance(tensor, np.ndarray):
            return tensor
        else:
            return np.array(tensor)