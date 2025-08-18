
import onnxruntime as ort
from transformers import AutoTokenizer
from pathlib import Path
import numpy as np


model_dir = Path("./models/llama-prompt-guard-onnx")
model_path = model_dir / "model.onnx"
model_name = str(model_dir)


tokenizer = AutoTokenizer.from_pretrained(model_name)
session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])


def _to_numpy(tensor):
    """Convert SparseTensor or ndarray to NumPy array."""
    if isinstance(tensor, ort.OrtValue):
        return tensor.numpy()
    elif hasattr(tensor, "to_dense"):  # For SparseTensor
        return tensor.to_dense().numpy()
    elif isinstance(tensor, np.ndarray):
        return tensor
    else:
        return np.array(tensor)

def predict_injecguard(text, threshold=0.5):
    # Tokenize input
    encoded = tokenizer(
        text, return_tensors="np", padding=True, truncation=True, max_length=256
    )

    # Match ONNX model’s expected input names
    ort_inputs = {
        k: v for k, v in encoded.items()
        if k in [i.name for i in session.get_inputs()]
    }

    # Run model
    outputs = session.run(None, ort_inputs)

    # Convert to NumPy (handles SparseTensor case)
    dense_outputs = [_to_numpy(o) for o in outputs]

    # Now safe to index
    logits = dense_outputs[0][0]
    prob_malicious = 1 / (1 + np.exp(-logits[1]))  # Assuming index 1 is "malicious"
    is_malicious = prob_malicious > threshold

    return {
        "score": float(prob_malicious),
        "is_malicious": bool(is_malicious)
    }
