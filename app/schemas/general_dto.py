from pydantic import BaseModel
from typing import Optional,List,Dict,Any
from app.schemas.general_enum import ThreatLevel
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
 
class AnalysisResult:
    content_type: str
    score: float
    is_malicious: bool
    threat_level: ThreatLevel
    details: Dict[str, Any]
    file_hash: Optional[str] = None
    file_size: Optional[int] = None            