from fastapi import FastAPI,HTTPException,UploadFile, File
from app.api.endpoints.ocr import process_files
from app.api.endpoints.document import manage_files
from app.utils.docker.download_model import download_model_from_blob 
from app.utils.global_security import set_predictor
#comment to test
app = FastAPI()
 

app.include_router(process_files.router,prefix="/api/v1/ocr",tags=["Upload files"])
app.include_router(manage_files.router,prefix="/api/v1/document",tags=["Manage files"])

@app.on_event("startup")
async def startup_event():
    # Download ONNX model if not cached
    model_path = download_model_from_blob()
 
    set_predictor(model_path=model_path)
 