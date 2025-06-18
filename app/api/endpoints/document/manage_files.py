from typing import Tuple 
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File
from app.core.settings import get_settings
from app.core.auth import get_api_key
from app.services.postgresql_db import save_doc_type_template,get_templates

router = APIRouter()

settings = get_settings()

@router.get("/list-documents", status_code=status.HTTP_200_OK,include_in_schema=True)
async def list_documents(countryId:int=3, api_key: str = Depends(get_api_key)):
    list_templates_db: list[Tuple[str, ...]]  = get_templates(countryId)
    return [(item[0], item[3]) for item in list_templates_db if len(item) > 2]

