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
from app.services.mistral_ocr import process_mistral_ocr,validate_document,process_azurevision_ocr
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
        content_type = str(file.content_type)
        file_name_uuid:str = f"{upload_file_id}-{file_name}"        
        #ocrResult = process_mistral_ocr(file_bytes,content_type) 
        ocrResult = process_azurevision_ocr(file_bytes)
        ocr_text = ocrResult['ocr_text']
        doc_type_code,score,doc_type_name = match_template(file_bytes,ocr_text,countryId)        
        if doc_type_code is None:
            raise HTTPException(status_code=400, detail=f"Document is not supported /upload {file_name}")     

        doc_type = DocumentType(doc_type_code)        
        result_openai_keywords = extract_keywords_openAI(doc_type, ocr_text)  

        result_scores = validate_document(result_openai_keywords,doc_type,RuleSet.general_rules,file_name,str(doc_type_name))

        if countryId == Country.brasil and doc_type==DocumentType.brasil_commercial_invoice:
          result_scores =  check_if_contains_beef(result_scores)

        # blob_path = f"{settings.cargologik_tenant}/{doc_type}/{file_name_uuid}"
        # blob_url_saved = save_file_blob_storage(file_bytes,"docmanagement",blob_path,settings.azure_storage_endpoint_cargologik)

        # container_client = get_container(settings.cosmos_endpoint_cl,settings.cosmos_key_cl,settings.cosmos_database_cl,settings.cosmos_container_doc_management_cl)        
        # est = pytz.timezone('America/New_York')
        # now = datetime.now(est)
        # est_time_string = now.strftime("%m/%d/%Y %I:%M:%S %p")
        # new_item = {  
        #     'id': str(uuid.uuid4()),          
        #     'name': filename,
        #     'type': content_type,
        #     'status': 'processed',
        #     'confidence': result_scores.get('doc_confidence'),
        #     'created_at_db':est_time_string,
        #     'blob_url': blob_url_saved,
        #     'ocr_text': ocrResult['ocr_text'],
        #     'tenantId':settings.providence_tenant,
        #     'documentType':doc_type,
        #     'created_at':est_time_string,
        #     'upload_file_id':upload_file_id
        # } 
        # container_client.upsert_item(body=new_item)

        # is_processed = True        
        return result_scores
    except HTTPException as exc:
        result_scores = {"error": exc.detail}
        # Let FastAPI handle it normally
        raise exc
        
    except Exception as exc:
        result_scores = {"error":exc.args} 
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )
    finally:
        save_doc_logs(upload_file_id,file_name,is_processed,doc_type,json.dumps(result_scores),settings.cargologik_tenant)

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
                list_pages = split_pdf(file_bytes,tenantId)
                doc_found = next((item for item in list_pages if item[0] == DocumentType.abf_freight_invoice), None)
                if doc_found:
                    #save the page regarding to template
                    doc_type_code,score,file_bytes,ocr_text = doc_found
            else:
                ocrResult = process_azurevision_ocr(file_bytes)              
                ocr_text = ocrResult['ocr_text']
                doc_type_code,score,doc_type_name = match_template(file_bytes,ocr_text,tenantId)    
        else:            
            ocrResult = process_azurevision_ocr(file_bytes)              
            ocr_text = ocrResult['ocr_text']
            doc_type_code,score,doc_type_name = match_template(file_bytes,ocr_text,tenantId)

        if doc_type_code is None:
             raise HTTPException(status_code=400, detail=f"Document is not supported /upload_freight_invoice {file_name}")             
        doc_type = DocumentType(doc_type_code)        
        result_openai_keywords = extract_keywords_openAI_freight_invoice(doc_type, ocr_text)  

        result_scores = validate_document(result_openai_keywords,doc_type,RuleSet.general_rules,file_name,str(doc_type_name))

        # blob_path = f"Load/{loadId}/processed_invoices/{file_name}"
        # blob_url_saved = save_file_blob_storage(file_bytes,"linkt",blob_path,settings.azure_storage_endpoint_providence)

        # container_client = get_container(settings.cosmos_endpoint_providence,settings.cosmos_key_providence,settings.cosmos_database_providence,settings.cosmos_container_providence)        
        # est = pytz.timezone('America/New_York')
        # now = datetime.now(est)
        # est_time_string = now.strftime("%m/%d/%Y %I:%M:%S %p")
        # new_item = {  
        #     'id': str(uuid.uuid4()),          
        #     'name': filename,
        #     'type': content_type,
        #     'status': 'processed',
        #     'confidence': result_scores.get('doc_confidence'),
        #     'created_at_db':est_time_string,
        #     'blob_url': blob_url_saved,
        #     'ocr_text': ocr_text,
        #     'tenantId':settings.providence_tenant,
        #     'documentType':doc_type,
        #     'created_at':est_time_string,
        #     'upload_file_id':upload_file_id,
        #     'loadId':loadId
        # }       
        # container_client.upsert_item(body=new_item)

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
        save_doc_logs(upload_file_id,file_name,is_processed,doc_type,json.dumps(result_scores),settings.providence_tenant,loadId)
   

@router.post("/save_template", status_code=status.HTTP_200_OK,include_in_schema=True)
async def save_template(file: UploadFile = File(...), doc_type:str='Master Bill of Lading',doc_type_code:str='',version:str='v1.0',country_id:int = 1,api_key: str = Depends(get_api_key)):   
    try:
        file_bytes = await file.read()
        content_type = str(file.content_type)
        #ocrResult = process_mistral_ocr(file_bytes,content_type)
        ocrResult = process_azurevision_ocr(file_bytes)    
        document_hash  = register_template(file_bytes,doc_type,version,country_id, ocrResult['ocr_text'],doc_type_code)
        return {f"Document save as temmplate successfully {document_hash}"}
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )    
    

@router.post("/get_text", status_code=status.HTTP_200_OK,include_in_schema=True)
async def get_text(file: UploadFile = File(...),api_key: str = Depends(get_api_key)):   
    try:
        file_bytes = await file.read()
        content_type = str(file.content_type)
        #ocrResult = process_mistral_ocr(file_bytes,content_type)
        ocrResult = process_azurevision_ocr(file_bytes)    

        ocr_text = ocrResult['ocr_text']

        doc_type_code,score,doc_type_name = match_template(file_bytes,ocr_text,2)

        return {"ocr_text":ocrResult['ocr_text'],"score":score}

    except Exception as exc:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                )
    


@router.post("/split_doc", status_code=status.HTTP_200_OK,include_in_schema=True)
async def split_doc(file: UploadFile = File(...),loadId:str = '',api_key: str = Depends(get_api_key)):    
   
    file_name:str = ''
    is_processed: bool = False
    doc_type: DocumentType = DocumentType.brasil_isf
    result_scores: Any = ""
    tenantId:int = 2
    try:
        file_bytes = await  file.read()
        filename = file.filename
       
        content_type = str(file.content_type) #'application/pdf'   
     
        doc_type_code:str|None = None
        score:float=0
        ocr_text:str=''
        ocrResult:Any
        if content_type=='application/pdf':
            input_stream = BytesIO(file_bytes)
            pdf_reader = PdfReader(input_stream)
            if len(pdf_reader.pages)>0:
                list_pages: List[Tuple[str | None, float, bytes, str]] = []
                list_pages = split_pdf(file_bytes,tenantId)
                for item in list_pages:
                    upload_file_id:str = str(uuid.uuid4())    
                    file_name = f"{upload_file_id}-{filename}"
                    doc_type_code,score,file_bytes,ocr_text = item
                    blob_path = f"{settings.cargologik_tenant}/{doc_type}/{file_name}"
                    blob_url_saved = save_file_blob_storage(file_bytes,"docmanagement",blob_path,settings.azure_storage_endpoint_cargologik)
        
        is_processed = True    
        return result_scores
    except HTTPException as exc:
        # Let FastAPI handle it normally
        raise exc
    except Exception as exc:
        result_scores = {"error":exc.args} 
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail= exc.args ,
                 ) 