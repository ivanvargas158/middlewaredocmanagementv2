
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

async def call_verify_document(pdf_bytes: bytes) -> dict: 
    page_images = []  
    # Step 1: Convert each page to an image and perform OCR
    page_images = await asyncio.to_thread(create_images_from_pdf, pdf_bytes) 
    # Step 2: Refine with Gemini using all page images
    return await verify_mbl_document(page_images)
 
    

async def verify_mbl_document(page_images: list) -> dict:
 
    prompt = """
    You are an expert logistics document analyst. Your primary task is to identify if the provided document is a Master Bill of Lading (MBL).
    Analyze the document image and determine its type based on the following criteria:
    1. Look for explicit titles: "Master Bill of Lading", "Bill of Lading", or "Ocean Bill of Lading".
    2. Identify the issuer: An MBL is issued directly by the ocean carrier (e.g., Maersk, MSC, CMA CGM, Hapag-Lloyd). Look for a prominent carrier logo or name.
    3. Check the shipper/consignee: In an MBL for a consolidated shipment, the shipper is often the origin agent/forwarder and the consignee is the destination agent/forwarder.
    4. Rule out other types: Ensure it is NOT a "House Bill of Lading (HBL)", "Forwarder's Bill of Lading", "Arrival Notice", "Packing List", or "Commercial Invoice". An HBL is issued by a freight forwarder or NVOCC.
    After your analysis, respond ONLY with a JSON object in the following format:
    {
        "document_type": "master_bill_of_lading",
        "confidence_score": <a number between 0.0 and 1.0>,
        "issuer_identified": "<Name of the carrier identified, or 'N/A'>",
        "reasoning": "<A brief explanation of your conclusion>"
    }
    If the document is not an MBL, set "document_type" to "House Bill of Lading", "Commercial Invoice", or "Other" and provide your reasoning.

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