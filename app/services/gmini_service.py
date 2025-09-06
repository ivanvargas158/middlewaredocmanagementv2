
import fitz 
import io
import re
import json
import asyncio
import logging
from PIL import Image
from app.utils.global_gmini import GeminiModegManager
from app.core.settings import get_settings
import google.generativeai as genai
from app.utils.soffice_utils import convert_with_soffice

settings = get_settings()

gmini = GeminiModegManager(settings.gmini_api_key)

logging.basicConfig(level=logging.ERROR)

async def get_gemini_vision_review(page_images: list, full_raw_text: str) -> str:
 
    prompt = f"""
    You are a document quality assurance specialist. Review the original document, provided as a series of page images, and correct the following raw OCR text that was extracted from it.
    Ensure the output is a perfect, clean transcription of the entire document. Fix all errors.
 
    --- FULL RAW OCR TEXT ---
    {full_raw_text}
    --- END FULL RAW OCR TEXT ---
 
    Return only the corrected, final text for the entire document.
    """
    # Create the content list for the multimodal request
    content = [prompt]
    content.extend(page_images) # Add all PIL image objects to the request
    gmini_model = gmini.get_model()   
    response = await gmini_model.generate_content_async(content)
    return response.text

async def call_verify_document(file_bytes: bytes,content_type:str) -> dict: 
    page_images = []  
    # Step 1: Convert each page to an image and perform OCR
    page_images = await asyncio.to_thread(create_images_from_file, file_bytes,content_type) 
    # Step 2: Refine with Gemini using all page images
    return await verify_mbl_document(page_images)
 
    

async def verify_mbl_document(page_images: list) -> dict:
 
    prompt = """
    You are an expert logistics document analyst. Your primary task is to identify if the provided document is a Master Bill of Lading (MBL).
 
    Analyze the document image and determine its type based on the following criteria:
 
    **DEFINITIVE MBL IDENTIFIERS (Any ONE of these confirms MBL):**
    1. **Ocean Carrier as Issuer**: Document issued by ocean vessel operating carriers such as:
       - Maersk (SCAC: MAEU), MSC (MSCU), CMA CGM (CMDU), Hapag-Lloyd (HLCU)
       - COSCO, Evergreen, ONE, Yang Ming, Zim, etc.
       - Look for SCAC codes (4-letter carrier codes like "MAEU")
    2. **"Signed for the Carrier [Ocean Carrier Name]"**: This phrase definitively indicates MBL
    3. **Vessel Information Present**: MBLs always contain:
       - Vessel name (e.g., "ROSA")
       - Voyage number (e.g., "531S")
       - Ocean ports for loading/discharge
 
    **DOCUMENT STRUCTURE INDICATORS:**
    - Title: "BILL OF LADING FOR OCEAN TRANSPORT OR MULTIMODAL TRANSPORT"
    - Container numbers in ocean format (e.g., MNBU0557767)
    - CY/CY (Container Yard to Container Yard) terms
    - Ocean freight terms and conditions
 
    **CRITICAL DISTINCTION RULES:**
    - **MBL**: Issued BY ocean carriers (even if shipper/consignee are forwarders)
    - **HBL**: Issued BY freight forwarders/NVOCCs referencing an underlying MBL
    - The ISSUER determines the document type, NOT the shipper/consignee identities
    **IGNORE THESE POTENTIAL CONFUSION FACTORS:**
    - Don't be misled if shipper/consignee appear to be logistics companies
    - Don't be confused by "As Agent" - this actually confirms MBL status
    - Multiple similar documents with same vessel/voyage are normal for consolidated shipments
    **NON-MBL DOCUMENTS:**
    - Freight forwarder letterhead/logos
    - "House Bill of Lading" in title
    - No vessel information
    - Trucking/rail bills of lading
    - Commercial invoices, packing lists, arrival notices
 
    Extract country of origin from the port of loading or shipper address.
 
    Respond ONLY with this JSON object:
    {
        "document_type": "master_bill_of_lading" | "house_bill_of_lading" | "commercial_invoice" | "other",
        "country_of_origin": "<country from port of loading/shipper, or 'Unknown'>",
        "confidence_score": <0.0 to 1.0>,
        "issuer_identified": "<Ocean carrier name or 'N/A'>",
        "scac_code": "<4-letter SCAC if visible, or 'N/A'>", 
        "vessel_voyage": "<vessel name and voyage if visible, or 'N/A'>",
        "key_identifier": "<primary reason for MBL classification>",
        "reasoning": "<Brief explanation focusing on the definitive MBL indicators found>"
    }
    """
    # Create the content list for the multimodal request
    content = [prompt]
    content.extend(page_images) # Add all PIL image objects to the request
    gmini_model = gmini.get_model()   
    response = await gmini_model.generate_content_async(content)
    response_text = getattr(response, 'text', '').strip()
    match = re.search(r'{.*}', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception as e:
            logging.error(f"Failed to parse JSON: {e} /raw_response: {response_text}")
            return {"error": f"Failed to parse JSON: {e}", "raw_response": response_text}
    else:
        return {"error": "No valid JSON object in Gemini response.", "raw_response": response_text}

async def refine_ocr_text(pdf_bytes: bytes, raw_ocr_text:str) -> str: 
    page_images = []  
    # Step 1: Convert each page to an image and perform OCR
    page_images = await asyncio.to_thread(create_images_from_pdf, pdf_bytes) 
    # Step 2: Refine with Gemini using all page images
    refined_text = await get_gemini_vision_review(page_images, raw_ocr_text)
 
    return refined_text


def create_images_from_pdf(pdf_bytes: bytes) -> list:
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_bytes))
        page_images.append(pil_image)

    return page_images
 


def create_images_from_file(file_bytes: bytes, content_type: str) -> list[Image.Image]:
    images = []

    if content_type == settings.AllowedMimeType.PDF.value:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            images.append(Image.open(io.BytesIO(img_bytes)))

    elif content_type in {
        settings.AllowedMimeType.PNG.value,
        settings.AllowedMimeType.JPEG.value,
        settings.AllowedMimeType.TIFF.value,
    }:
        img = Image.open(io.BytesIO(file_bytes))
        img_converted = img.convert("RGB") if img.mode != "RGB" else img
        images.append(img_converted)

    elif content_type in {
        settings.AllowedMimeType.DOC.value,
        settings.AllowedMimeType.DOCX.value,
        settings.AllowedMimeType.XLS.value,
        settings.AllowedMimeType.XLSX.value,
    }:
        # Convert Office file → PDF
        origin_ext = {
            settings.AllowedMimeType.DOC.value: ".doc",
            settings.AllowedMimeType.DOCX.value: ".docx",
            settings.AllowedMimeType.XLS.value: ".xls",
            settings.AllowedMimeType.XLSX.value: ".xlsx",
        }[content_type]

        pdf_bytes = convert_with_soffice(file_bytes, origin_ext, ".pdf")
        return create_images_from_file(pdf_bytes, settings.AllowedMimeType.PDF.value)

    else:
        raise ValueError(f"Unsupported file type: {content_type}")

    return images
