import re
from enum import Enum
from typing import Dict, List, Set
from .general_enum import DocumentType
from app.schemas.general_dto import ErrorValidationRules 
from app.utils.custom_exceptions import ValidationError
class RuleSet(str, Enum):
    general_rules = "general"



general_rules = {
    DocumentType.commercial_invoice: {
        "required_fields": {
                       "invoice_number": r"^.+$",  # Non-empty string
                        "invoice_date": r"^.+$",  # Non-empty string
                        "exporter": r"^.+$",  # Non-empty string
                        "consignee": r"^.+$",  # Non-empty string
                        "country_of_origin": r"^.+$",  # Non-empty string
                        "country_of_destination": r"^.+$",  # Non-empty string
                        "currency": r"^.+$",  # Non-empty string
                        "total_invoice_value": r"^[1-9]\d*(\.\d+)?$",  # Positive number (int or float)
                        "description_of_goods": r"^.+$",  # Non-empty string
                        "quantity": r"^[1-9]\d*$",  # Positive integer
                        "unit_price": r"^.+$",  # Non-empty string
                },
        "cross_field_rules": []  # Add rules if needed
    },
    DocumentType.master_bill_of_lading: {
        "required_fields": ["bill_of_lading_number",
                            "shipper",
                            "consignee",
                            "vessel_name",
                            "port_of_loading",
                            "port_of_discharge",
                            "gross_weight",
                            "number_of_packages",
                            "description_of_goods",
                            "date_of_issue",
                            "place_of_issue",
                            "carrier"]
    },    
    DocumentType.one_ocean_master_bill_of_lading: {
        "required_fields": ["bill_of_lading_number",
                            "shipper",
                            "consignee",
                            "vessel_name",
                            "voyage_number",
                            "port_of_loading",
                            "port_of_discharge",
                            "number_and_kind_of_packages",
                            "description_of_goods",
                            "gross_weight",
                            "date_of_issue",
                            "place_of_issue",
                            "carrier",
                            "signature"]
                            },
    DocumentType.packing_list_swift: {
        "required_fields": {
                    "packing_slip_number": r"^.+$",  # Non-empty string
                    "exporter": r"^.+$",
                    "consignee": r"^.+$",
                    "date": r"^.+$",
                    "port_of_loading": r"^.+$",
                    "port_of_discharge": r"^.+$",
                    "description_of_goods": r"^.+$",
                    "number_of_packages": r"^[1-9]\d*$",  # Integer > 0
                    "gross_weight": r"^[1-9]\d*(\.\d+)?$",  # Float > 0
                    "swift_facility": r"^.+$",
                    "signature_and_stamp": r"^.+$" 
                    },
        "cross_field_rules": []  # Add rules if needed
    },
    DocumentType.packing_list_minerva: {
        "required_fields": ["packing_list_number",
                            "exporter",
                            "consignee",
                            "date",
                            "port_of_loading",
                            "port_of_discharge",
                            "description_of_goods",
                            "number_of_packages",
                            "gross_weight",
                            "minerva_plant",
                            "signature_and_stamp"]
    },
    DocumentType.health_certificate_argentina:{
         "required_fields": [
                   "certificate_number",
                    "exporter",
                    "consignee",
                    "country_of_origin",
                    "country_of_destination",
                    "date_of_issue",
                    "product_description",
                    "quantity",
                    "ministry_authority",
                    "signature_and_stamp"
         ]

    },
    DocumentType.health_certificate_brasil:{
         "required_fields": [
                   "certificate_number",
                    "exporter",
                    "consignee",
                    "country_of_origin",
                    "country_of_destination",
                    "date_of_issue",
                    "product_description",
                    "quantity",
                    "ministry_authority",
                    "signature_and_stamp"
         ]

    },
    DocumentType.nop_import_certificate:{
         "required_fields": [
                   "certificate_number",
                    "exporter",
                    "importer",
                    "consignee",
                    "country_of_origin",
                    "country_of_destination",
                    "date_of_issue",
                    "product_description",
                    "quantity",
                    "organic_status",
                    "certification_body",
                    "signature_and_stamp"
         ]

    },
    DocumentType.certificate_of_origin:{
         "required_fields": [
                   "certificate_number",
                    "exporter",
                    "consignee",
                    "country_of_origin",
                    "country_of_destination",
                    "date_of_issue",
                    "product_description",
                    "quantity",
                    "minerva_plant",
                    "signature_and_stamp"
                        ]

    },
     DocumentType.certificate_of_analysis:{
         "required_fields": [
                   "certificate_number",
                    "date_of_issue",
                    "exporter",
                    "consignee",
                    "product_name",
                    "batch_lot_number",
                    "quantity",
                    "test_parameters",
                    "test_results",
                    "conclusion",
                    "minerva_plant",
                    "signature_and_stamp"
                        ]

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
    },
    DocumentType.abf_freight_invoice:{
        "required_fields": {
                "invoice_number": r"^.+$",  # Non-empty string
                "pro_number": r"^.+$",      # Non-empty string
                "total_invoice_amount_usd": r"^[1-9]\d*(\.\d+)?$",  # Float > 0
                "reference_numbers.po_number": r"^.+$",  # Non-empty string
                "reference_numbers.bill_of_lading_number": r"^.+$",  # Non-empty string
                "ship_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
                "invoice_due_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
                "total_piece_count": r"^[1-9]\d*$",  # Integer > 0
                "total_weight_lbs": r"^[1-9]\d*$",  # Integer > 0
                "weight_lbs": r"^[1-9]\d*$",  # Integer > 0
                "piece_count": r"^[1-9]\d*$"  # Integer > 0
            },
            "cross_field_rules": []
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
        raise ValidationError(errors,doc_type=doc_type,ocr_mapped_fields=data)
    
    return data


def validate_single_field(schema_class, field_name: str, value):
    try:
        # Create partial input with just the field to validate
        validated = schema_class(**{field_name: value})
        return 1.0, "OK"
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        return 0.5, f"Validation error: {error_msg}"
    
# score, reason = validate_single_field(DangerousGoodsSchema, "un_number", "UN1234")
# print(score, reason)  # Output: 1.0, OK