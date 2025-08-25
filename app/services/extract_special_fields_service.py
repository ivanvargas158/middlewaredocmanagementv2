
import re
from app.schemas.general_dto import ShipmentDetails
from typing import Optional,List 


async def extract_mbl_shipment_details(document_text: str,schema_json_mbl_doc):
    details = await extract_shipment_details_from_mbl(document_text)
    if details.scac_code:
        schema_json_mbl_doc["scac_code"] = details.scac_code
    if details.mode:
        schema_json_mbl_doc["mode"] = details.mode
    if details.service_type:
        schema_json_mbl_doc["service_type"] = details.service_type
      
    return  schema_json_mbl_doc

async def extract_shipment_details_from_mbl(document_text: str) -> ShipmentDetails:
 
    
    details = ShipmentDetails()
    text_upper = document_text.upper()
    text_lines = document_text.split('\n')
    
    # Step 1: Identify transportation mode
    details.mode = await identify_transport_mode(text_upper)
    
    # Step 2: Extract SCAC code using multiple strategies
    details.scac_code = await _extract_scac_code(document_text, text_upper)
    
    # Step 3: Determine service type for ocean shipments
    if details.mode == 'ship':
        details.service_type = await _extract_service_type(text_upper)
    
    # Step 4: Extract commodity information
    #details.commodity = await _extract_commodity(document_text, text_lines)
    
    # Step 5: Extract container numbers
    #details.container_numbers = await _extract_container_numbers(text_upper, text_lines)
    
    # Step 6: Extract carrier name
    #details.carrier_name = await _extract_carrier_name(text_lines)
    
    return details

 
async def identify_transport_mode(text_upper: str) -> str: 
    # Ocean indicators (weighted by reliability)
    ocean_indicators = [
        ('SEA WAYBILL', 10),
        ('BILL OF LADING', 10),
        ('OCEAN', 8),
        ('VESSEL', 8),
        ('PORT OF LOADING', 8),
        ('PORT OF DISCHARGE', 8),
        ('FCL', 7),
        ('LCL', 7),
        ('CONTAINER', 6),
        ('SHIPPED ON BOARD', 6),
        ('MULTIMODAL TRANSPORT', 5),
    ]
 
    # Air indicators
    air_indicators = [
        ('AIR WAYBILL', 10),
        ('AIRWAY BILL', 10),
        ('AIR CARGO', 8),
        ('AIRPORT', 7),
        ('FLIGHT', 6),
        ('PIECE', 5),
    ]
 
    # Land indicators (road & rail)
    land_indicators = [
        ('CMR', 10),
        ('ROAD CONSIGNMENT NOTE', 9),
        ('TRUCK', 8),
        ('TRUCKING', 8),
        ('FTL', 7),
        ('LTL', 7),
        ('RAIL WAYBILL', 9),
        ('RAIL CONSIGNMENT NOTE', 9),
        ('INLAND BILL OF LADING', 8),
        ('HAULAGE', 6),
    ]
 
    # Score calculation
    ocean_score = sum(weight for indicator, weight in ocean_indicators if indicator in text_upper)
    air_score = sum(weight for indicator, weight in air_indicators if indicator in text_upper)
    land_score = sum(weight for indicator, weight in land_indicators if indicator in text_upper) 
    # Decide based on max score
    scores = {'ship': ocean_score, 'plane': air_score, 'land': land_score}
    return max(scores.keys(), key=lambda k: scores[k])

 

async def _extract_scac_code(document_text: str, text_upper: str) -> Optional[str]:
 
    
    # Strategy 1: Look for explicit SCAC field
    scac_patterns = [
        r'SCAC[:\s]*([A-Z]{4})',
        r'CARRIER CODE[:\s]*([A-Z]{4})',
        r'SCAC CODE[:\s]*([A-Z]{4})',
    ]
    
    for pattern in scac_patterns:
        match = re.search(pattern, text_upper)
        if match:
            return match.group(1)
    
    # Strategy 2: Extract from common reference number patterns
    # Many carriers embed SCAC in waybill/booking numbers
    reference_patterns = [
        r'(?:SWB-NO|WAYBILL|BOOKING)[:\s]*([A-Z]{4})[A-Z0-9]+',
        r'([A-Z]{4})[A-Z]{2}\d{10}',  # Pattern like HLCUAS0250701089
        r'([A-Z]{4})\d{10,}',
        r'BL[:\s]*([A-Z]{4})[A-Z0-9]+',
    ]
    
    for pattern in reference_patterns:
        matches = re.findall(pattern, text_upper)
        for match in matches:
            if await _validate_scac_code(match):
                return match
    
    # Strategy 3: Look for 4-letter codes near carrier names or in structured fields
    # Extract potential SCAC codes from document structure
    lines = document_text.upper().split('\n')
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['CARRIER', 'SHIPPING LINE', 'AGENT']):
            # Look in current line and next few lines for 4-letter codes
            search_lines = lines[i:i+3]
            for search_line in search_lines:
                four_letter_codes = re.findall(r'\b([A-Z]{4})\b', search_line)
                for code in four_letter_codes:
                    if await _validate_scac_code(code):
                        return code
    
    # Strategy 4: Pattern matching in container numbers (some carriers include SCAC)
    container_patterns = [
        r'([A-Z]{4})\s*\d{7}',  # Standard container format
        r'CONTAINER[:\s]*([A-Z]{4})',
    ]
    
    for pattern in container_patterns:
        matches = re.findall(pattern, text_upper)
        for match in matches:
            if await _validate_scac_code(match):
                return match
    
    return None

async def _validate_scac_code(code: str) -> bool:
  
    if len(code) != 4 or not code.isalpha():
        return False
    
    # Exclude common false positives
    excluded_codes = {
        'FROM', 'WITH', 'DATE', 'CODE', 'SAID', 'SUCH', 'BILL', 'PORT',
        'LOAD', 'SHIP', 'CONT', 'PACK', 'SEAL', 'MARK', 'PAGE', 'ITEM',
        'RATE', 'PAID', 'FREE', 'HELD', 'VOID', 'NULL', 'TRUE', 'FALSE',
        'MULT'
    }
    
    return code not in excluded_codes

async def _extract_service_type(text_upper: str) -> Optional[str]:
     
    if 'FCL/FCL' in text_upper or 'FCL' in text_upper:
        return 'FCL'
    elif 'LCL/LCL' in text_upper or 'LCL' in text_upper:
        return 'LCL'
    elif 'CONTAINER' in text_upper and ('FULL' in text_upper or 'COMPLETE' in text_upper):
        return 'FCL'
    
    return None

async def _extract_commodity(document_text: str, text_lines: List[str]) -> Optional[str]:
     
    # Look for goods description patterns
    commodity_keywords = [
        'DESCRIPTION OF GOODS', 'COMMODITY', 'CARGO', 'GOODS',
        'MERCHANDISE', 'PRODUCT', 'CONTENTS'
    ]
    
    for i, line in enumerate(text_lines):
        line_upper = line.upper()
        if any(keyword in line_upper for keyword in commodity_keywords):
            # Look for description in current and next few lines
            for j in range(i, min(i + 5, len(text_lines))):
                desc_line = text_lines[j].strip()
                if desc_line and not any(kw in desc_line.upper() for kw in commodity_keywords):
                    # Clean up common noise
                    if len(desc_line) > 10 and not desc_line.isdigit():
                        return desc_line
    
    # Alternative: Look for specific product mentions
    product_patterns = [
        r'(\d+\s+(?:CARTONS?|BOXES?|PACKAGES?)\s+[A-Z\s]+)',
        r'(FROZEN\s+[A-Z\s]+)',
        r'(BEEF\s+[A-Z\s]+)',
        r'([A-Z\s]*MEAT[A-Z\s]*)',
    ]
    
    for pattern in product_patterns:
        match = re.search(pattern, document_text.upper())
        if match:
            return match.group(1).strip()
    
    return None

async def _extract_container_numbers(text_upper: str, text_lines: List[str]) -> List[str]:
    """Extract container numbers from the document."""
    
    container_numbers = []
    
    # Standard container number patterns
    patterns = [
        r'([A-Z]{4}\s*\d{7})',  # Standard format like HLBU 9959346
        r'CONTAINER[:\s]*([A-Z]{4}\s*\d{7})',
        r'CONT[:\s]*([A-Z]{4}\s*\d{7})',
    ]
    
    for line in text_lines:
        for pattern in patterns:
            matches = re.findall(pattern, line.upper())
            for match in matches:
                clean_number = re.sub(r'\s+', '', match)
                if clean_number not in container_numbers:
                    container_numbers.append(clean_number)
    
    return container_numbers

async def _extract_carrier_name(text_lines: List[str]) -> Optional[str]:
     
    # Look in first few lines for carrier name
    for line in text_lines[:10]:
        line_clean = line.strip()
        if ('AKTIENGESELLSCHAFT' in line_clean.upper() or 
            'SHIPPING' in line_clean.upper() or
            'MARITIME' in line_clean.upper() or
            'LINES' in line_clean.upper()):
            return line_clean
    
    return None