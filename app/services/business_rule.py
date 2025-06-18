from typing import Dict, Tuple, List,Any

def check_if_contains_beef(json_response: Dict[str, Any]) -> Dict[str, Any]:
 
    line_items = json_response.get("all_fields", {}).get("line_items", [])
    
    for item in line_items:
        description = item.get("description_of_goods", "")
        if "BEEF" in description.upper():
            json_response["required_coa"] = True
            return json_response
    json_response["required_coa"] = False
    return json_response