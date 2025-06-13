from enum import Enum


class DocumentType(str, Enum):
    air_waybill = "air_waybill"
    dangerous_goods = "dangerous_goods"    
    commercial_invoice = "commercial_invoice" 
    master_bill_of_lading = "master_bill_of_lading"
    one_ocean_master_bill_of_lading = "one_ocean_master_bill_of_lading"
    packing_list_swift = "packing_list_swift"
    packing_list_minerva = "packing_list_minerva"
    argentina_health_certificate = "argentina_health_certificate" 
    brasil_health_certificate = "brasil_health_certificate"    
    nop_import_certificate = "nop_import_certificate"
    certificate_of_origin = "certificate_of_origin"
    certificate_of_analysis = "certificate_of_analysis"
    brasil_certificate_of_analysis = "brasil_certificate_of_analysis"
    brasil_isf = "brasil_isf"
    abf_freight_invoice  = "abf_freight_invoice"