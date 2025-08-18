from pathlib import Path
import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np


predictor_instance = None   

class Predictor:
    _instance = None
    def __new__(cls, model_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model(model_path)
        return cls._instance

    def _init_model(self, model_path):
        if model_path is None or not Path(model_path).exists():
            raise FileNotFoundError(f"ONNX model not found at {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])

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
        ort_inputs = {k: v for k, v in encoded.items() if k in [i.name for i in self.session.get_inputs()]}
        outputs = self.session.run(None, ort_inputs)
        dense_outputs = [self._to_numpy(o) for o in outputs]
        logits = dense_outputs[0][0]
        prob_malicious = 1 / (1 + np.exp(-logits[1]))
        return {"score": float(prob_malicious), "is_malicious": prob_malicious > threshold}

 


def set_predictor(model_path):
    global predictor_instance
    predictor_instance = Predictor(model_path)

def get_predictor():
    if predictor_instance is None:
        raise RuntimeError("Predictor not initialized. Did the startup event run?")
    return predictor_instance