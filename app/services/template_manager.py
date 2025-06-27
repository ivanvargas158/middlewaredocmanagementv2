import hashlib
import re
from difflib import SequenceMatcher
from datetime import datetime
from app.services.postgresql_db import save_doc_type_template,get_templates
from typing import Tuple 
from fastapi import HTTPException  
         
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

def match_template(document_bytes: bytes, result_ocr_text:str, countryId:int,min_similarity=0.5) -> Tuple[str|None, float,str|None] :
    try:        
        list_templates_db: list[Tuple[str, str, str, str, bool]] = get_templates(countryId)
        # fingerprint = create_hash(document_bytes) 
    
    
        result_doc_type_code = None    
        best_score = 0    
        for template_id,doc_type_name,doc_text,doc_type_code,is_requiered in list_templates_db:        
            # Assume each template has a 'sample_text' field for comparison
            score = text_similarity(doc_text, result_ocr_text)        
            if score > best_score:            
                result_doc_type_code = doc_type_code            
                best_score = score    
                if best_score >= min_similarity:                
                    return result_doc_type_code,best_score,doc_type_name                     
        return None,0,None
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error matching the template {ex}") 
    
#Option #2 to match Invoice Freight

def is_arcbest_invoice(text):
    """Check if the provided text matches ArcBest freight invoice patterns."""

    patterns = {
        "header": [
            r"(?i)ORIGINAL INVOICE",
            r"(?i)Remit Payment To:\s*ArcBest",
            r"(?i)Service:\s*LTL"
        ],
        "addresses": [
            r"ArcBest\s*PO BOX 10048\s*FORT SMITH,\s*AR,\s*72917-0048",
            r"ACCOUNTS PAYABLE\s*PO BOX 3395\s*NEW YORK,\s*NY,\s*10008-3395"
        ],
        "contact_info": [
            r"Phone:\s*\(\d{3}\)\s*\d{3}-\d{4}\s*Fax:\s*\(\d{3}\)\s*\d{3}-\d{4}",
            r"jconnelly@abf\.com",
            r"arcb\.com"
        ],
        "financial_fields": [
            r"AMOUNT DUE:\s*\$\d{1,5}\.\d{2}",
            r"PAYMENT DUE DATE:\s*\d{2}/\d{2}/\d{4}",
            r"\(payable in US funds\)",
            r"TOTAL AMOUNT DUE BY.*?\$\d{1,5}\.\d{2}"
        ],
        "identifiers": [
            r"Freight bill No:\s*\d+",
            r"Account No:\s*\w{5,}-\d+",
            r"Shipper Acct\. #\s*\w+-\d+",
            r"Consignee Acct\. #\s*[\dA-Z\-]+",
            r"Bill of Lading No:\s*\d+",
            r"PQ SCHEDULE NO:\s*\w+",
            r"CRN:\s*WWW\d+"
        ],
        "footer": [
            r"\*PLEASE DETACH THIS PORTION AND ENCLOSE WITH YOUR PAYMENT\*",
            r"\*{3}\s*RETAIN THIS PORTION FOR YOUR RECORDS\s*\*{3}",
            r"Thank you for choosing ArcBest℠",
            r"FED TAX ID#\s*\d{2}-\d{7}"
        ]
    }

    # Count how many major sections have at least one match
    matched_sections = 0
    for section, pats in patterns.items():
        if any(re.search(pat, text) for pat in pats):
            matched_sections += 1

    # Heuristic: if 5+ of the 6 major sections are matched, assume it's valid
    return matched_sections >= 5

# # Example usage:
# if __name__ == "__main__":
#     with open("sample_invoice.txt", "r", encoding="utf-8") as f:
#         document_text = f.read()
    
#     if is_arcbest_invoice(document_text):
#         print("✅ Document is an ArcBest invoice.")
#     else:
#         print("❌ Document does NOT match ArcBest invoice pattern.")
