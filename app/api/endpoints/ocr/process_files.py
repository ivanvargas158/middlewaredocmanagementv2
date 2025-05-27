import json
import pytz
import uuid
import os
from typing import Any
from datetime import datetime
from app.services.blob_storage import save_file_blob_storage
#from app.services.mistral_ocr import process_mistral_ocr,validate_document,process_azurevision_ocr
from app.services.cosmos_db import get_container
from app.services.open_ai import extract_keywords_openAI,extract_keywords_openAI_freight_invoice
#from app.services.template_manager import register_template,match_template 
from app.services.postgresql_db import save_doc_logs
from app.schemas.general_enum import DocumentType
from app.core.settings import get_settings
from app.core.auth import get_api_key
from app.schemas.validation_rules import validate_against_rules,RuleSet
from app.utils.custom_exceptions import ValidationError
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File

router = APIRouter()

settings = get_settings()

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(file: UploadFile = File(...),api_key: str = Depends(get_api_key)):    
    upload_file_id:str = str(uuid.uuid4())
   
    try:
         
        return upload_file_id
    except ValidationError as exc:
        content_ocr = exc.to_dict()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.to_dict()
        )
    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )
    # finally:
    #     save_doc_logs(upload_file_id,file_name,is_processed,doc_type,json.dumps(content_ocr))

@router.post("/upload_freight_invoice", status_code=status.HTTP_200_OK)
async def upload_freight_invoice(file: UploadFile = File(...),api_key: str = Depends(get_api_key)):    
    upload_file_id:str = str(uuid.uuid4())
    try:
         
        return upload_file_id
    except ValidationError as exc:
        content_ocr = exc.to_dict()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.to_dict()
        )
    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )
    # finally:
    #     save_doc_logs(upload_file_id,file_name,is_processed,doc_type,json.dumps(content_ocr))


def validate_file_type(filename: str, content_type: str):
    ext = os.path.splitext(filename)[1].lower()
    if content_type not in settings.allowed_mime_types:
        raise ValidationError(errors=f"Unsupported file type: {content_type}")
    if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]:
        raise ValidationError(errors=f"Unsupported file extension: {ext}")

def validate_file_size(file_bytes: bytes):
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_file_size:
        raise ValidationError(errors=f"File size exceeds {settings.max_file_size} MB limit.")
    
 