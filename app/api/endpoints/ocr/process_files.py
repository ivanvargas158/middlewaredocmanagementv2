import json
import uuid
from typing import Any
from app.services.business_rule import validate_document
from app.services.open_ai import extract_keywords_openAI
from app.services.template_manager import register_template,match_template 
from app.services.postgresql_db import save_doc_logs
from app.services.handle_file import validate_file_type,validate_file_size
from app.services.business_rule import check_if_contains_beef
from app.schemas.general_enum import DocumentType,Country,ProcessExtractionType
from app.core.settings import get_settings
from app.core.auth import get_api_key
from app.schemas.validation_rules import RuleSet
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File
from app.services.gmini_service import refine_ocr_text
from app.services.azure_ocr_service import azure_ocr_async
from app.utils.global_resources import mime_type_to_extractor 
from app.services.chat_gpt_service import create_request
from app.utils.global_security import get_predictor
router = APIRouter()

settings = get_settings()

model  = get_predictor()

@router.post("/upload", status_code=status.HTTP_200_OK,include_in_schema=True)
async def upload_file(file: UploadFile = File(...),countryId:int=3,process_extraction_type:int =ProcessExtractionType.process_and_validate, api_key: str = Depends(get_api_key)):    
    upload_file_id:str = str(uuid.uuid4())
    file_name:str = ''
    is_processed: bool = False
    doc_type: DocumentType = DocumentType.air_waybill
    result_scores: dict = {}
    result_text: str = ''
    try:
        file_bytes = await  file.read()
        if file.filename:
            file_name = file.filename
        validate_file_type(str(file.filename), str(file.content_type))
        validate_file_size(file_bytes)         
        content_type = str(file.content_type)                 
        if content_type in settings.mime_types_office:
            extractor = mime_type_to_extractor.get(str(file.content_type))           
            if extractor:
                result_text = await extractor(file_bytes, str(file.filename))
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type {file.content_type}")
        else:
            ocrResult:dict = await azure_ocr_async(file_bytes)
            ocr_text = ocrResult['ocr_text']
            result_text =  await refine_ocr_text(file_bytes,ocr_text)

        result_scanner = model.predict(result_text)

        if result_scanner["is_malicious"]:
             return {
                    "is_injection_document_risk": True                    
                }
        
        if process_extraction_type == ProcessExtractionType.process_and_validate:    
            doc_type_code,score,doc_type_name = await match_template(file_bytes,result_text,countryId)        
            if doc_type_code is None:
                raise HTTPException(status_code=400, detail=f"Document is not supported /upload {file_name}")     

            doc_type = DocumentType(doc_type_code)        
            result_openai_keywords = await extract_keywords_openAI(doc_type, result_text)  

            result_scores = validate_document(result_openai_keywords,doc_type,RuleSet.general_rules,file_name,str(doc_type_name))

            if countryId == Country.brasil and doc_type==DocumentType.brasil_commercial_invoice:
                result_scores =  check_if_contains_beef(result_scores)

        else:
            result_json_schema:str =  await create_request(result_text,settings.fc_agent_api_key,settings.fc_agent_process_text_uuid,True)
            result_scores = json.loads(result_json_schema)
            result_scores["documents"][0]["file_name"] = file_name
            result_scores["is_injection_document_risk"] = False
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


@router.post("/save_template", status_code=status.HTTP_200_OK,include_in_schema=True)
async def save_template(file: UploadFile = File(...), doc_type:str='Master Bill of Lading',doc_type_code:str='',version:str='v1.0',country_id:int = 1,api_key: str = Depends(get_api_key)):   
    ocr_text_final:str = ''
    try:
        file_bytes = await file.read()
        content_type = str(file.content_type)
        if content_type in settings.mime_types_office:
            extractor = mime_type_to_extractor.get(content_type)           
            if extractor:
                ocr_text_final = await extractor(file_bytes, str(file.filename))
        else:
            ocrResult = await azure_ocr_async(file_bytes) 
            ocr_text_final =  await refine_ocr_text(file_bytes,ocrResult['ocr_text'])   
        document_hash  = await register_template(file_bytes,doc_type,version,country_id, ocr_text_final,doc_type_code)
        return {f"Document save as temmplate successfully {document_hash}"}
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )   

 