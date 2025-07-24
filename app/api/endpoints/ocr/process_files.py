import json
import uuid
import pytz
from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfReader
from typing import Any
from typing import List,Tuple
from app.services.cosmos_db import get_container
from app.services.blob_storage import save_file_blob_storage
from app.services.business_rule import validate_document
from app.services.open_ai import extract_keywords_openAI,extract_keywords_openAI_freight_invoice
from app.services.template_manager import register_template,match_template 
from app.services.postgresql_db import save_doc_logs
from app.services.handle_file import validate_file_type,validate_file_size,split_pdf
from app.services.business_rule import check_if_contains_beef
from app.schemas.general_enum import DocumentType,Country
from app.core.settings import get_settings
from app.core.auth import get_api_key
from app.schemas.validation_rules import RuleSet
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File
from app.services.gmini_service import refine_ocr_text
from app.services.azure_ocr_service import azure_ocr_async
router = APIRouter()

settings = get_settings()

@router.post("/upload", status_code=status.HTTP_200_OK,include_in_schema=True)
async def upload_file(file: UploadFile = File(...),countryId:int=3, api_key: str = Depends(get_api_key)):    
    upload_file_id:str = str(uuid.uuid4())
    file_name:str = ''
    is_processed: bool = False
    doc_type: DocumentType = DocumentType.air_waybill
    result_scores: Any = ""
    try:
        file_bytes = await  file.read()
        if file.filename:
            file_name = file.filename
        validate_file_type(str(file.filename), str(file.content_type))
        validate_file_size(file_bytes)         
      
        ocrResult = await azure_ocr_async(file_bytes)
        ocr_text = ocrResult['ocr_text']

        refined_ocr_text:str =  await refine_ocr_text(file_bytes,ocr_text)
        
        doc_type_code,score,doc_type_name = await match_template(file_bytes,refined_ocr_text,countryId)        
        if doc_type_code is None:
            raise HTTPException(status_code=400, detail=f"Document is not supported /upload {file_name}")     

        doc_type = DocumentType(doc_type_code)        
        result_openai_keywords = await extract_keywords_openAI(doc_type, refined_ocr_text)  

        result_scores = validate_document(result_openai_keywords,doc_type,RuleSet.general_rules,file_name,str(doc_type_name))

        if countryId == Country.brasil and doc_type==DocumentType.brasil_commercial_invoice:
          result_scores =  check_if_contains_beef(result_scores)

        
        return result_scores
    except HTTPException as exc:
        result_scores = {"error": exc.detail} 
        raise exc
        
    except Exception as exc:
        result_scores = {"error":exc.args} 
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )
    finally:
        await save_doc_logs(upload_file_id,file_name,is_processed,doc_type,json.dumps(result_scores),settings.cargologik_tenant)

@router.post("/upload_freight_invoice", status_code=status.HTTP_200_OK,include_in_schema=True)
async def upload_freight_invoice(file: UploadFile = File(...),loadId:str = '',api_key: str = Depends(get_api_key)):    
    upload_file_id:str = str(uuid.uuid4())
    file_name:str = ''
    is_processed: bool = False
    doc_type: DocumentType = DocumentType.abf_freight_invoice
    result_scores: Any = ""
    tenantId:int = 2
    try:
        file_bytes = await  file.read()
        filename = file.filename
        validate_file_type(str(file.filename), str(file.content_type))
        validate_file_size(file_bytes)
        content_type = str(file.content_type) #'application/pdf'       
        file_name = f"{upload_file_id}-{filename}"
        doc_type_code:str|None = None
        doc_type_name:str|None = None
        score:float=0
        ocr_text:str=''
        ocrResult:Any
        if content_type=='application/pdf':
            input_stream = BytesIO(file_bytes)
            pdf_reader = PdfReader(input_stream)
            if len(pdf_reader.pages)>1:
                list_pages: List[Tuple[str | None, float, bytes, str]] = []
                list_pages = await split_pdf(file_bytes,tenantId)
                doc_found = next((item for item in list_pages if item[0] == DocumentType.abf_freight_invoice), None)
                if doc_found:
                    #save the page regarding to template
                    doc_type_code,score,file_bytes,ocr_text = doc_found
            else:
                ocrResult = await azure_ocr_async(file_bytes)              
                ocr_text = ocrResult['ocr_text']
                doc_type_code,score,doc_type_name = await match_template(file_bytes,ocr_text,tenantId)    
        else:            
            ocrResult = await azure_ocr_async(file_bytes)              
            ocr_text = ocrResult['ocr_text']
            doc_type_code,score,doc_type_name = await match_template(file_bytes,ocr_text,tenantId)
        
        if doc_type_code is None:
             raise HTTPException(status_code=400, detail=f"Document is not supported /upload_freight_invoice {file_name}")             
        doc_type = DocumentType(doc_type_code)        
        result_openai_keywords = await extract_keywords_openAI_freight_invoice(doc_type, ocr_text)  

        result_scores = validate_document(result_openai_keywords,doc_type,RuleSet.general_rules,file_name,str(doc_type_name))

        is_processed = True    
        return result_scores
    except HTTPException as exc:
        result_scores = {"error": exc.detail}
        raise exc
    except Exception as exc:
        result_scores = {"error":exc.args} 
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                 )
    finally:
        await save_doc_logs(upload_file_id,file_name,is_processed,doc_type,json.dumps(result_scores),settings.providence_tenant,loadId)
   

@router.post("/save_template", status_code=status.HTTP_200_OK,include_in_schema=True)
async def save_template(file: UploadFile = File(...), doc_type:str='Master Bill of Lading',doc_type_code:str='',version:str='v1.0',country_id:int = 1,api_key: str = Depends(get_api_key)):   
    try:
        file_bytes = await file.read()
        content_type = str(file.content_type)
        #ocrResult = process_mistral_ocr(file_bytes,content_type)
        ocrResult = await azure_ocr_async(file_bytes) 
        refined_ocr_text:str =  await refine_ocr_text(file_bytes,ocrResult['ocr_text'])   
        document_hash  = await register_template(file_bytes,doc_type,version,country_id, refined_ocr_text,doc_type_code)
        return {f"Document save as temmplate successfully {document_hash}"}
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )    
      