import re
from enum import Enum
from typing import Dict, List, Set
from .general_enum import DocumentType
from fastapi import HTTPException
class RuleSet(str, Enum):
    general_rules = "general"



general_rules = {
    
    DocumentType.brasil_health_certificate: {
        "required_fields": {
            "exporter": r"^.+$",                    
            "certificate_number": r"^.+$",                             
            "competent_authority": r"^.+$",
            "local_competent_authority": r"^.+$",
            "importer": r"^.+$",
            "country_of_origin": r"^.+$",
            "origin_iso_code": r"^[A-Z]{2,3}$",
            "country_of_dispatch": r"^.+$",
            "dispatch_iso_code": r"^[A-Z]{2,3}$",
            "country_of_destination": r"^.+$",
            "destination_iso_code": r"^[A-Z]{2,3}$",
            "place_of_loading": r"^.+$",
            "means_of_transport": r"^.+$",
            "point_of_entry": r"^.+$",
            "conditions_for_transport_storage": r"^.+$",
            "container_seal_numbers": r"^.+$",
            "shipping_marks": r"^.+$",
            "food_producers": r"^.+$",
            "purpose": r"^.+$",
            "ncm_hs_code": r"^\d{4,10}$",  # Adjusted for common NCM/HS code lengths
            "certificate_reference_number": r"^.+$",
            "carteira_fiscal_number": r"^.+$",

            "product_details[].product_description": r"^.+$",
            "product_details[].animal_species": r"^.+$",
            "product_details[].lot_or_production_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date
            "product_details[].slaughter_date": r"^\d{4}-\d{2}-\d{2}$",         # ISO date
            "product_details[].producer_approval_number": r"^.+$",
            "product_details[].type_of_packaging": r"^.+$",
            "product_details[].number_of_packages": r"^\d+$",
            "product_details[].net_weight_kgs": r"^\d+([.,]\d+)?$",
            "product_details[].net_weight_lbs": r"^\d+([.,]\d+)?$"
        }
    },
    DocumentType.brasil_master_bill_of_lading:{
         "required_fields": {
            "bill_of_lading_no": r"^.+$",                    # non-empty string
            "shipper_name": r"^.+$",                              # non-empty string
            "shipper_address": r"^.+$",                              # non-empty string
            "consignee_name": r"^.+$",                            # non-empty string
            "consignee_address": r"^.+$",                            # non-empty string
            "notify_parties": r"^.+$",                        # non-empty string
            "vessel_and_voyage_no": r"^.+$",                  # non-empty string
            "port_of_loading": r"^.+$",                        # non-empty string
            "port_of_discharge": r"^.+$",                      # non-empty string
            "container_numbers": r"^.+$",                      # string inside array, each item non-empty
            "description_of_packages_and_goods": r"^.+$",     # non-empty string
            "gross_cargo_weight": r"^[\d.,\s]+$",              # numbers, dots, commas, spaces (e.g. "17,012.50")
            "total_items": r"^\d+$",                            # integer (digits only)
            "total_gross_weight": r"^[\d.,\s]+$",              # numbers, dots, commas, spaces
            "net_weight": r"^[\d.,\s]+$",                       # numbers, dots, commas, spaces
            "gross_weight": r"^[\d.,\s]+$",                     # numbers, dots, commas, spaces
            "shipped_on_board_date": r"^\d{4}-\d{2}-\d{2}$",   # date YYYY-MM-DD
            "freight_charges": {
                "rate": r"^.+$",                                # non-empty string
                "prepaid": r"^.+$",                               # non-empty string
                "collect": r"^.+$",                               # non-empty string
                "terminal_handling_charge": r"^.+$"              # numbers, dots, commas, spaces
            },
            "place_and_date_of_issue": r"^.+$",                 # non-empty string
            "container_cargo_table[].container_numbers": r"^.+$",
            "container_cargo_table[].seal_numbers": r"^.+$",
            "container_cargo_table[].marks_and_numbers": r"^.+$",
            "container_cargo_table[].description_of_packages_and_goods": r"^.+$",
            "container_cargo_table[].gross_cargo_weight": r"^[\d.,\s]+$",
            "container_cargo_table[].measurement": r"^.+$",
            "container_cargo_table[].net_weight": r"^[\d.,\s]+$",
            "container_cargo_table[].gross_weight": r"^[\d.,\s]+$",
            "container_cargo_table[].ncm": r"^.+$",
            "container_cargo_table[].hs_code": r"^.+$",
            "container_cargo_table[].seal_sif": r"^.+$",
            "container_cargo_table[].temperature": r"^.+$",
            "container_cargo_table[].ruc": r"^.+$",   

            "packagesInfo[].packageType": r"^.+$",  # Non-empty string
            "packagesInfo[].amount":  r"^[\d.,\s]+$",  # Non-empty string
            "totalVolume": r"^[\d.,\s]+$",
            "totalVolumeUnit": r"^.+$", 
         }
    },

    DocumentType.brasil_isf: {
        "required_fields": {
            "seller_name_address": r"^.+$",
            "buyer_name_address": r"^.+$",
            "ship_to_party": r"^.+$",
            "container_stuffing_location": r"^.+$",
            "importer_of_record": r"^.+$",
            "manufacturer_name_address": r"^.+$",
            "consignee": r"^.+$",
            "country_of_origin": r"^.+$",
            "commodity_description": r"^.+$",
            "vessel_voyage": r"^.+$",
            "bill_of_lading_number": r"^.+$",
            "container_number": r"^[A-Z]{4}\d{7}$",  # Standard container number format (e.g., ABCD1234567)
            "etd": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
            "eta": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
        }
    },
    DocumentType.brasil_certificate_of_analysis: {
        "required_fields": {
            "loaded_date": r"^\d{4}-\d{2}-\d{2}$",             # ISO date format (YYYY-MM-DD)
            "container_number": r"^[A-Z]{4}\d{7}$",            # Standard container number format (ABCD1234567)
            "shipping_mark": r"^.+$",                          # Non-empty string
            "customer": r"^.+$",                               # Non-empty string
            "destination": r"^.+$",                            # Non-empty string
            "contract_number": r"^.+$",                        # Non-empty string
            "net_weight_kg": r"^\d{1,3}(\.\d{3})*,\d{2}$",                 # Positive float or integer
            "microbiological_results[].product_code": r"^.+$",
            "microbiological_results[].batch_lot": r"^.+$",
            "microbiological_results[].result_ecoli_o157_h7": r"^.+$",
            "microbiological_results[].result_salmonella": r"^.+$"		
        }
    },
    DocumentType.brasil_commercial_invoice: {
        "required_fields": {
            "issuing_country": r"^.+$",
            "invoice_number": r"^.+$",
            "invoice_date": r"^\d{4}-\d{2}-\d{2}$",
            "importer_details": r"^.+$",
            "ocean_vessel": r"^.+$",
            "port_of_loading": r"^.+$",
            "port_of_discharge": r"^.+$",
            "payment_terms": r"^.+$",
            "importer_ref": r"^.+$",
            "shipping_mark": r"^.+$",
            "signer_cpf": r"^.+$",

            "line_items[].description_of_goods": r"^.+$",
            "line_items[].net_weight_kgs": r"^\d+(\.\d+)?$",
            "line_items[].unit_price_usd_per_kgs": r"^\d+(\.\d+)?$",
            "line_items[].amount_usd": r"^\d+(\.\d+)?$",

            "totals[].description": r"^.+$",
            "totals[].currency": r"^[A-Z]{3}$",  # e.g., USD, BRL
            "totals[].amount": r"^\d+(\.\d+)?$",

            "container_details[].container_id": r"^.+$",
            "container_details[].net_weight_details": r"^.+$",
            "container_details[].gross_weight_details": r"^.+$",
            "container_details[].carton_count": r"^\d+$",

            "intermediary_bank": r"^.+$",
            "intermediary_aba": r"^.+$",
            "intermediary_swift": r"^[A-Z0-9]{8,11}$",
            "beneficiary_bank": r"^.+$",
            "beneficiary_bank_address": r"^.+$",
            "beneficiary_swift": r"^[A-Z0-9]{8,11}$",
            "beneficiary_account_number": r"^.+$",
            "beneficiary_name": r"^.+$"
        }
    },
    DocumentType.brasil_certificate_of_origin: {
        "required_fields": {
            "issuing_country": r"^.+$",  # string
            "certificate_number": r"^.+$",  # string
            "exporter": r"^.+$",  # string
            "importer": r"^.+$",  # string
            "importer_ref": r"^.+$",  # string
            "shipping_mark": r"^.+$",  # string
            "vessel": r"^.+$",  # string
            "shipment_port": r"^.+$",  # string
            "destination": r"^.+$",  # string
            "total_net_weight_kgs_summary": r"^\d+(\.\d+)?$",  # number
            "total_gross_weight_kgs_summary": r"^\d+(\.\d+)?$",  # number
            "total_cartons_summary": r"^\d+$",  # integer
            "container_id_summary": r"^.+$",  # string
            "total_weight": r"^\d+(\.\d+)?$",  # number
            "signer_cpf": r"^.+$",  # string
            "issue_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format
            "issue_location": r"^.+$",  # string
            "goods_description[].cartons": r"^\d+$",  # integer
            "goods_description[].description": r"^.+$",  # string
            "goods_description[].net_weight_kgs": r"^\d+(\.\d+)?$",  # number
            "container_details[].container_id": r"^.+$",  # string
            "container_details[].net_weight_kgs": r"^\d+(\.\d+)?$",  # number
            "container_details[].gross_weight_kgs": r"^\d+(\.\d+)?$",  # number
            "container_details[].cartons": r"^\d+$"  # integer
        }
    },
    DocumentType.brasil_packing_list: {
        "required_fields": {  
            "issuing_country": r"^.+$",  
            "packing_list_number": r"^.+$",
            "packing_list_date": r"^.+$",
            "importer_details": r"^.+$",
            "ocean_vessel": r"^.+$",
            "port_of_loading": r"^.+$",
            "port_of_discharge": r"^.+$",
            "importer_ref": r"^.+$",
            "shipping_mark": r"^.+$",
            "signer_cpf": r"^.+$",
            "line_items[].description_of_goods": r"^.+$",
            "line_items[].net_weight_kgs": r"^.+$",
            "line_items[].gross_weight_kgs": r"^.+$",
            "line_items[].cartons": r"^.+$",
            "container_summary[].container_id": r"^.+$",
            "container_summary[].net_weight_kgs": r"^.+$",
            "container_summary[].gross_weight_kgs": r"^.+$",
            "container_summary[].cartons": r"^.+$"
        }
    },
    DocumentType.air_waybill: {
        "required_fields": ["mawb", "hawb", "gross_weight", "shipper"],
        "dangerous_goods": {
            "un_number_format": r"^UN\d{4}$",
            "allowed_hazard_classes": ["3", "4", "8", "9"],
            "prohibited_materials": [
                "explosives", 
                "radioactive_materials"
            ]
        },
        "weight": {
            "unit": "kg",
            "max_value": 1000  # kg
        },
        "special_handling_codes": [
            "FRAGILE", "PERISHABLE", "THIS_SIDE_UP"
        ]
    }, 
    DocumentType.paraguay_export_package:{
             "required_fields": {  
                "documentNumber": r"^.+$",  
                "issueDate": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format,   
             }

    },
    DocumentType.paraguay_sea_waybill:{
             "required_fields": {  
                "seaWaybillNumber": r"^.+$",  
                "issueDate": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format
             }
    },
    DocumentType.paraguay_health_certificate:{
             "required_fields": {  
                "certificateNumber": r"^.+$",  
                "issueDate": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format
             }
    },
    DocumentType.paraguay_certificate_analysis:{
             "required_fields": {  
                "certificateNumber": r"^.+$",  
                "issueDate": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format
             }
    },
    DocumentType.dangerous_goods: {
        "required_fields": ["un_number", "proper_shipping_name", "emergency_contacts"],
        "packaging_standards": {
            "container_types": ["1A1", "1A2", "4G"],
            "max_quantity_per_package": 1000  # liters/kg based on class
        },
        "emergency_info": {
            "required_contacts": 2,
            "24hr_contact": True
        }
    }
     
}

PROHIBITED_MATERIALS: Set[str] = {
    "explosives", "radioactive_materials", "chemical_weapons"
}

def get_validation_rules(doc_type: DocumentType, rule_set: RuleSet) -> Dict:
    """Get compliance rules for document type and regulation set"""
    rule_map = {
        RuleSet.general_rules: general_rules
    }
    return rule_map[rule_set].get(doc_type, {})

def validate_un_number_format(un_number: str) -> bool:
    """Validate UN number against IATA/IMO format requirements"""
    return re.match(r"^UN\d{4}$", un_number) is not None

def check_prohibited_materials(description: str) -> List[str]:
    """Check material descriptions against global prohibited list"""
    return [
        material for material in PROHIBITED_MATERIALS 
        if material in description.lower()
    ]
 

def validate_against_rules(data: Dict, doc_type: DocumentType, rule_set: RuleSet) -> Dict:
    """Main validation entry point"""
    rules = get_validation_rules(doc_type, rule_set)
    #result_errors = ErrorValidationRules()
    errors = []

    # Check required fields
    missing_fields = [
        field for field in rules.get("required_fields", [])
        if field not in data or data[field] is None
    ]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")

    # Document-type specific validations
    if doc_type == DocumentType.air_waybill:
        if "dangerous_goods" in data:
            dg_data = data["dangerous_goods"]
            if not validate_un_number_format(dg_data.get("un_number", "")):
                errors.append("Invalid UN number format")
            
            if prohibited := check_prohibited_materials(dg_data.get("description", "")):
                errors.append(f"Prohibited materials: {', '.join(prohibited)}")

    elif doc_type == DocumentType.dangerous_goods:
        # IMO-specific validations
        pass

    if errors:
        raise HTTPException(status_code=500, detail=errors)
    
    return data

 