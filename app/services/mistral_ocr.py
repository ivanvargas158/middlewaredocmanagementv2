import base64
import time
import logging
import re
from typing import Dict, Tuple, List
from datetime import datetime
from typing import Dict, Any,Union
from mistralai import Mistral
from io import BytesIO 
from datetime import date
from decimal import Decimal
from app.core.settings import get_settings
from app.schemas.validation_rules import get_validation_rules,RuleSet
from app.schemas.general_enum import DocumentType
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.core.exceptions import HttpResponseError
from azure.cognitiveservices.vision.computervision.models import ComputerVisionOcrError
from msrest.authentication import CognitiveServicesCredentials
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

def file_to_base64(file_bytes) -> str:   
    encoded_bytes = base64.b64encode(file_bytes)
    return encoded_bytes.decode("utf-8")

def process_mistral_ocr(file_bytes:bytes, file_type: str) -> Dict[str, Any]:
     
    ocr_applied:str = "mistral"
    mistral_client = Mistral(api_key=settings.mstral_api_Key)
    base64_data = file_to_base64(file_bytes)
    file_type_key = 'pdf' if file_type == 'application/pdf' else 'image'        
    if file_type_key == 'pdf':
        ocr_response = mistral_client.ocr.process(
            model=settings.mistral_ocr_model,
            document={
                "type": "document_url",
                "document_url": f"data:{file_type};base64,{base64_data}" 
            }
        )
    else:
        ocr_response = mistral_client.ocr.process(
            model=settings.mistral_ocr_model,
            document={
                "type": "image_url",
                "image_url": f"data:{file_type};base64,{base64_data}" 
            }
        )                     

    full_text = ""
    for page in ocr_response.pages:           
        full_text += page.markdown + "\n"
    confidence:int = 0
    if "![img-0.jpeg](img-0.jpeg)" in full_text:            
        try:
            result_azurevision_ocr = process_azurevision_ocr(file_bytes)
            full_text = result_azurevision_ocr["ocr_text"]
            confidence = result_azurevision_ocr["ocr_confidence"]
            ocr_applied = "azure"
        except HTTPException as exc:
            raise HTTPException(status_code=500, detail=f"{exc}")
        

    ocr_result = {
        "ocr_text": full_text,
        "ocr_confidence": confidence,
        "metadata": {
            "documentType": file_type_key,
            "pageCount": len(ocr_response.pages)
        },
        "ocr_applied":ocr_applied,
        "ocr_response": ocr_response
    }

    return ocr_result

   
 

def process_azurevision_ocr(file_bytes:bytes):

    try:

        computervision_client = ComputerVisionClient(settings.azurevision_endpoint, CognitiveServicesCredentials(settings.azurevision_subscription_key))

        read_response = computervision_client.read_in_stream(BytesIO(file_bytes), raw=True)

        if not read_response or not hasattr(read_response, "headers"):
            raise HTTPException(status_code=500,detail="Azure Read API response is invalid. Check your file and credentials.")

        read_operation_location = read_response.headers["Operation-Location"]

        if not read_operation_location:
            raise HTTPException(status_code=500,detail="Azure Operation-Location header missing from response.")

        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results 
        while True:
            read_result = computervision_client.get_read_result(operation_id)  
                    
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        #Print the detected text, line by line
        if read_result.status == OperationStatusCodes.succeeded:
            extracted_text = []
            total_confidence = 0.0
            word_count = 0
            for page in read_result.analyze_result.read_results:
                for line in page.lines:
                    line_text = []
                    extracted_text.append(line.text)
                    for word in line.words:
                        line_text.append(word.text)
                        total_confidence += word.confidence
                        word_count += 1
            average_confidence = (total_confidence / word_count) if word_count > 0 else 0.0
            return {
                "ocr_text": "\n".join(extracted_text),
                "ocr_confidence": round(average_confidence, 3)
            }
        
        else:
            raise HTTPException(status_code=500,detail="Azure OCR Failed")

    except HttpResponseError as e:

        error_message = e.message or str(e)
        if e.response is not None and hasattr(e.response, 'text') and e.response.text:
            error_message += f" | Response: {e.response.text}"
        logger.error(f"Azure Vision API error: {error_message}")
        raise HTTPException(status_code=500,detail=f"Azure Vision API error: {error_message}")
    
    except Exception as ex:
        raise HTTPException(status_code=500,detail=f"Unexpected error during Azure OCR: {str(ex)}")

    


# --- Gibberish/Symbol Detection ---
def is_gibberish(text: str) -> bool:
    if not text:
        return False
    non_alpha = sum(1 for c in text if not c.isalnum() and c not in " .,-/")
    if len(text) > 0 and (non_alpha / len(text)) > 0.3:
        return True
    if re.search(r'(.)\1{8,}', text):  # 5+ repeated chars
        return True
    if re.search(r'[\uFFFD\u25A0\u25A1]', text):  # common OCR replacement chars
        return True
    return False


# --- Field Scoring ---
def score_fieldv2(value: str, required: bool = True) -> Tuple[float, str]:
    if not value or not str(value).strip():
        return (0.0, "Missing" if required else "Optional/Missing")
    if is_gibberish(str(value)):
        return (0.2, "Gibberish/symbols detected")
    return (1.0, "OK")

def score_field(value: Union[str, int, float, Decimal, date], pattern: str) -> Tuple[float, str]:
    value_str = str(value).strip() if value is not None else ""
    if not value_str:
        return 0.0, "Missing"
    if is_gibberish(value_str):
        return 0.2, "Gibberish/symbols detected"
    if re.match(pattern, value_str,re.DOTALL):
        return 1.0, "OK"
    return 0.5, "Format mismatch"

# --- Main Document Validation ---
def validate_document(flat_fields: Dict[str, str], doc_type_code:DocumentType,rule_set:RuleSet,file_name:str,doc_type_name:str, threshold=0.95)-> Dict[str, Any]:
  
    rules = get_validation_rules(doc_type_code, rule_set)
    required_fields = rules.get("required_fields", [])
    cross_field_rule_names = rules.get("cross_field_rules", [])
    # Required fields from rules

    # Score each required field (presence and gibberish check)
    field_scores = {}
    missing_fields = []   
    value:Any
    score:float = 0
    for field,pattern in required_fields.items():
        if '[]' in field:
            base_path, sub_field = field.split('[]')
            base_path = base_path.strip('.')
            array_data = get_nested_value(base_path, flat_fields)

            if isinstance(array_data, list):
                for index, item in enumerate(array_data):
                    value = get_nested_value(sub_field.strip('.'), item)
                    field_key = f"{base_path}[{index}].{sub_field.strip('.')}"
                    score, reason = score_field(value, pattern)
                    field_scores[field_key] = (score, reason, value)
                    if reason == 'Missing' or reason == 'Gibberish/symbols detected':
                        missing_fields.append(field_key)
        else:
          
            value = get_nested_value(field,flat_fields)
            process_field(field,value,pattern,field_scores,missing_fields)
            
    # Schema-level validation
    cross_issues = [] 
    cross_penalty = 0.0
    cross_issues = []
    for rule_name in cross_field_rule_names:
        rule_func = CROSS_FIELD_RULES.get(rule_name) #If we need to add validations rules for some field. Modify the Enum and cross_field_rules
        if rule_func:
            penalty, issue = rule_func(flat_fields)
            if penalty > 0:
                cross_penalty += penalty
                cross_issues.append(issue)
                logging.warning(f"Cross-field issue: {issue}")

    # Compute document confidence
    scores = [score for score, _, _ in field_scores.values()]
    base_score = sum(scores) / len(scores) if scores else 0.0
    cross_penalty = 0.1 * len(cross_issues)
    doc_confidence = round(max(0.0, base_score - cross_penalty),2)
    pass_flag = doc_confidence >= threshold

    return {
        "doc_type_code": doc_type_code,
        "doc_type_name": doc_type_name,
        "doc_confidence": doc_confidence,
        "missing_fields": missing_fields,        
        "pass": pass_flag,
        "all_fields":flat_fields,
        "file_name": file_name
    }

def process_field(field, value, pattern, field_scores, missing_fields):
    def handle_score(subkey, val, pat):
        score, reason = score_field(val, pat)
        field_scores[subkey] = (score, reason, val)
        if reason in ('Missing', 'Gibberish/symbols detected'):
            missing_fields.append(subkey)

    if isinstance(value, dict):
        for key, subfield_value in value.items():
            subfield_key = f'{field}/{key}'
            subfield_pattern = pattern.get(key, None)
            if subfield_pattern is not None:
                handle_score(subfield_key, subfield_value, subfield_pattern)
    else:
        handle_score(field, value, pattern)


def get_nested_value(field_path: str, data: dict):
    keys = field_path.split('.')
    
    def recursive_get(keys_list, current_data):
        if not keys_list or current_data is None:
            return current_data
        return recursive_get(keys_list[1:], current_data.get(keys_list[0]))
    
    return recursive_get(keys, data)


# --- Cross-field Logic Implementations ---
def invoice_date_not_future(fields: Dict[str, str]) -> Tuple[float, str]:
    date_str = fields.get("Invoice Date")
    if date_str:
        try:
            date_val = datetime.strptime(date_str, "%Y-%m-%d")
            if date_val > datetime.now():
                return 0.2, "Invoice Date is in the future"
        except Exception:
            return 0.2, "Invoice Date parsing failed"
    return 0.0, ""
 
def net_weight_positive(fields: Dict[str, str]) -> Tuple[float, str]:
    weight_str = fields.get("Net weight (Kg)")
    if weight_str:
        try:
            weight_val = float(re.sub(r"[^\d.,]", "", weight_str).replace(",", "."))
            if weight_val <= 0:
                return 0.2, "Net weight is not positive"
        except Exception:
            return 0.2, "Net weight parsing failed"
    return 0.0, ""
 
def issue_date_not_future(fields: Dict[str, str]) -> Tuple[float, str]:
    date_str = fields.get("Issue Date")
    if date_str:
        try:
            date_val = datetime.strptime(date_str, "%Y-%m-%d")
            if date_val > datetime.now():
                return 0.2, "Issue Date is in the future"
        except Exception:
            return 0.2, "Issue Date parsing failed"
    return 0.0, ""

CROSS_FIELD_RULES = {
    "invoice_date_not_future": invoice_date_not_future,
    "net_weight_positive": net_weight_positive,
    "issue_date_not_future": issue_date_not_future,
    # Add more as needed
}


 