from fastapi import FastAPI,HTTPException,UploadFile, File
from app.api.endpoints.ocr import process_files
from app.api.endpoints.document import manage_files
from app.api.endpoints.gmailwebhook import webhook
#comment to test
app = FastAPI()

app.include_router(process_files.router,prefix="/api/v1/ocr",tags=["Upload files"])
app.include_router(manage_files.router,prefix="/api/v1/document",tags=["Manage files"])
app.include_router(webhook.router,prefix="/api/v1/webhook",tags=["Gmail Webhook"])