from pydantic import BaseModel

class Shipper(BaseModel):
    name: str
    
class ShippingDocument(BaseModel):
    mawb: str
    hawb: str
    gross_weight: float
    shipper: Shipper
    type: str  # Required for validation, e.g., "air_waybill", "dangerous_goods"

class ErrorValidationRules():
    errors = []
    required_fields: str
    doc_type: str