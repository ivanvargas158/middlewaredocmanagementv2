from fastapi import FastAPI,HTTPException,UploadFile, File
from app.api.endpoints.ocr import process_files
from app.api.endpoints.document import manage_files
from app.utils.global_security import InjectionGuardModel

#comment to test
app = FastAPI()
model = InjectionGuardModel()


app.include_router(process_files.router,prefix="/api/v1/ocr",tags=["Upload files"])
app.include_router(manage_files.router,prefix="/api/v1/document",tags=["Manage files"])


@app.on_event("startup")
async def startup_event():
    # Initialize model once when FastAPI starts
    await model.init()
    model.predict("hello world -  test injection guard")