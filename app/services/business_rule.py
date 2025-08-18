import re
from decimal import Decimal
from datetime import date,datetime
from typing import Dict, Tuple, List,Any,Union
from app.schemas.general_enum import DocumentType
from app.schemas.validation_rules import get_validation_rules,RuleSet

def check_if_contains_beef(json_response: Dict[str, Any]) -> Dict[str, Any]:
 
    line_items = json_response.get("all_fields", {}).get("line_items", [])
    
    for item in line_items:
        description = item.get("description_of_goods", "")
        if "BEEF" in description.upper():
            json_response["required_coa"] = True
            return json_response
    json_response["required_coa"] = False
    return json_response




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
        "file_name": file_name,
        "is_injection_document_risk": False    
    }


def get_nested_value(field_path: str, data: dict):
    keys = field_path.split('.')
    
    def recursive_get(keys_list, current_data):
        if not keys_list or current_data is None:
            return current_data
        return recursive_get(keys_list[1:], current_data.get(keys_list[0]))
    
    return recursive_get(keys, data)




def score_field(value: Union[str, int, float, Decimal, date], pattern: str) -> Tuple[float, str]:
    value_str = str(value).strip() if value is not None else ""
    if not value_str:
        return 0.0, "Missing"
    if is_gibberish(value_str):
        return 0.2, "Gibberish/symbols detected"
    if re.match(pattern, value_str,re.DOTALL):
        return 1.0, "OK"
    return 0.5, "Format mismatch"


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