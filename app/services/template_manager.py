import hashlib
from difflib import SequenceMatcher
from datetime import datetime
from app.services.postgresql_db import save_doc_type_template,get_templates
from app.utils.custom_exceptions import ValidationError
from typing import Tuple 
  
         
def create_hash(document_bytes: bytes) -> str:
    """Create normalized document fingerprint using multi-hash strategy"""
    try:
        sha256 = hashlib.sha256()    
        sha256.update(document_bytes)   
        return sha256.hexdigest()
    except Exception as e:
        raise ValueError(f"Image processing failed: {str(e)}")

def register_template(document_bytes: bytes,doc_type:str,version:str,tenent_id:int,doc_text:str,doc_type_code:str) -> str:
    """Store document template with security checks"""
    try:
        document_hash = create_hash(document_bytes)
        save_doc_type_template(document_hash,doc_type,version,tenent_id,doc_text,doc_type_code)
        return document_hash
    except Exception as e:
        raise ValueError(f"Error saving the template: {str(e)}")     
 

# async def find_template(document_bytes: bytes, threshold: float = 0.9) -> str:
#     """Find matching document template with similarity check"""
#     result:str=''

#     query_hash = await create_hash(document_bytes)
    
#     templates = await get_templates()
#     for template_id,doc_type in templates:
#         if (template_id==query_hash):
#             result = f"FP: {template_id} - doc type: {doc_type}"
#     return result


def text_similarity(a: str, b: str) -> float:
    # Simple ratio, replace with more advanced NLP if needed 
    return SequenceMatcher(None, a, b).ratio()

def match_template(document_bytes: bytes, result_ocr_text:str, tenantId:int,min_similarity=0.6) -> Tuple[str|None, float] :
    try:        
        list_templates_db: list[Tuple[str, ...]]  = get_templates(tenantId)
        fingerprint = create_hash(document_bytes) 
        
        # 1. Exact hash match   
        result = next((item for item in list_templates_db if item[0] == fingerprint), None)
        if result is not None:         
            return result[3],1

        # 2. Fuzzy text match    
    
        result_doc_type_code = None    
        best_score = 0    
        for template_id,doc_type,doc_text,doc_type_code in list_templates_db:        
            # Assume each template has a 'sample_text' field for comparison
            score = text_similarity(doc_text, result_ocr_text)        
            if score > best_score:            
                result_doc_type_code = doc_type_code            
                best_score = score    
                if best_score >= min_similarity:                
                    return result_doc_type_code,best_score                      
        return None,0
    except Exception as ex:
        raise ValidationError(f"Error matching the template {ex}") 
    
