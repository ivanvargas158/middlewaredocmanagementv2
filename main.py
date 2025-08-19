from fastapi import FastAPI
from app.api.endpoints.ocr import process_files
from app.api.endpoints.document import manage_files
from app.utils.docker.download_model import download_model_from_blob 
from app.utils.global_security import set_predictor
import traceback
from pathlib import Path
import sys

app = FastAPI()
 

app.include_router(process_files.router,prefix="/api/v1/ocr",tags=["Upload files"])
app.include_router(manage_files.router,prefix="/api/v1/document",tags=["Manage files"])

@app.on_event("startup")
async def startup_event():    
    try:       
        #model_path = download_model_from_blob()
        if sys.platform == "win32":
         # local Windows dev
            model_path = Path("./app/models/llama-prompt-guard-onnx")
        else:
            # Docker / Linux
            model_path = Path("/app/models/llama-prompt-guard-onnx")     
        set_predictor(model_path=model_path)
    except Exception as e:
        print("Startup failed with exception:")
        traceback.print_exc()
        raise
 