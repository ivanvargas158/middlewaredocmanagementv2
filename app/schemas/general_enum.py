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
    ef_doc_type_ci_1  = "ef_doc_type_ci_1"
    ef_pdf_invoice_1  = "ef_pdf_invoice_1"
    ef_xls_type_4  = "ef_xls_type_4"
    ef_xls_type_isf_3  = "ef_xls_type_isf_3"
    ef_xlsx_type_ci_1  = "ef_xlsx_type_ci_1"
    ef_xlsx_type_isf_2  = "ef_xlsx_type_isf_2"

class Country(int, Enum):
    brasil = 3

class ProcessExtractionType(int, Enum):
    process_and_validate = 1
    extract_text = 2
    