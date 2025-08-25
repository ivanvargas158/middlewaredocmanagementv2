from pydantic import BaseModel
from typing import Optional,List
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


class ShipmentDetails:
    scac_code: Optional[str] = None
    mode: Optional[str] = None  # 'AIR' or 'OCEAN'
    service_type: Optional[str] = None  # 'FCL', 'LCL', or None for air
    commodity: Optional[str] = None
    container_numbers: Optional[List[str]] = None
    carrier_name: Optional[str] = None
    
    def __post_init__(self):
        if self.container_numbers is None:
            self.container_numbers = []