# pyright: reportPrivateImportUsage=false

import google.generativeai as genai
from threading import Lock

class GeminiModegManager:
    _instance = None
    _lock = Lock()
    model: genai.GenerativeModel = None  # type: ignore

    def __new__(cls, api_key: str):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    genai.configure(api_key=api_key)  # Safe to use
                    cls._instance = super().__new__(cls)
                    cls._instance.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        return cls._instance

    def get_model(self):
        return self.model
