from fastapi import FastAPI,HTTPException,UploadFile, File
from app.api.endpoints.ocr import process_files
#comment to test
app = FastAPI()

app.include_router(process_files.router,prefix="/api/v1/ocr",tags=["Upload files"])
 