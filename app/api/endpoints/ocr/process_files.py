import json
import uuid
from app.services.template_manager import register_template 
from app.services.postgresql_db import save_doc_logs
from app.services.handle_file import validate_file_type,validate_file_size
from app.schemas.general_enum import DocumentType
from app.core.settings import get_settings
from app.core.auth import get_api_key
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File
from app.services.gmini_service import refine_ocr_text,call_verify_document
from app.services.azure_ocr_service import azure_ocr_async
from app.services.extract_special_fields_service import extract_mbl_shipment_details
from app.utils.global_resources import mime_type_to_extractor 
from app.services.chat_gpt_service import create_request
from app.utils.global_security import async_predict
router = APIRouter()

settings = get_settings()



@router.post("/upload", status_code=status.HTTP_200_OK,include_in_schema=True)
async def upload_file(file: UploadFile = File(...),api_key: str = Depends(get_api_key)):    
    upload_file_id:str = str(uuid.uuid4())
    file_name:str = ''
    is_processed: bool = False
    doc_type: DocumentType = DocumentType.air_waybill
    result_scores: dict = {}
    result_verification:dict = {}
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
            result_verification = await call_verify_document(file_bytes)  

        result_scanner = await async_predict(result_text)

        if result_scanner["is_malicious"]:
             return {
                    "is_injection_document_risk": True                    
                }
        
        result_json_schema:str =  await create_request(result_text,settings.fc_agent_api_key,settings.fc_agent_process_text_uuid,True)
        result_scores = json.loads(result_json_schema)
        if result_verification['document_type'] == DocumentType.master_bill_of_lading:
            result_scores = await extract_mbl_shipment_details(result_text,result_scores)
        result_scores["file_name"] = file_name
        result_scores["is_injection_document_risk"] = False
        result_scores["document_type"] = result_verification['document_type'] if 'document_type' in result_verification else 'Unknown'
        result_scores["country_of_origin"] = result_verification['country_of_origin'] if 'country_of_origin' in result_verification else 'Unknown'

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

 