from enum import Enum

class DocumentType(str, Enum):
    air_waybill = "air_waybill"
    dangerous_goods = "dangerous_goods"         
    brasil_certificate_of_analysis = "brasil_certificate_of_analysis"
    brasil_isf = "brasil_isf"
    brasil_health_certificate = "brasil_health_certificate"
    brasil_master_bill_of_lading = "brasil_master_bill_of_lading"
    brasil_commercial_invoice = "brasil_commercial_invoice"
    brasil_packing_list = "brasil_packing_list"
    brasil_certificate_of_origin = "brasil_certificate_of_origin"
    brasil_master  = "brasil_master"
    paraguay_export_package = "pr_export_document_package"
    paraguay_sea_waybill = "pr_sea_waybill"
    paraguay_health_certificate = "pr_health_certificate"
    paraguay_certificate_analysis = "pr_certificate_analysis"
    master_bill_of_lading = "master_bill_of_lading"

class Country(int, Enum):
    brasil = 3

class ProcessExtractionType(int, Enum):
    process_and_validate = 1
    extract_text = 2
    