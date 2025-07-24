
import fitz 
import io
from PIL import Image
from app.utils.global_gmini import GeminiModegManager
from app.core.settings import get_settings
import google.generativeai as genai

settings = get_settings()

gmini = GeminiModegManager(settings.gmini_api_key)

 
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

async def refine_ocr_text(pdf_bytes: bytes, raw_ocr_text:str) -> str:
 
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_images = []
    ocr_texts = []
    # Step 1: Convert each page to an image and perform OCR
 
    for page_num   in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_bytes))
        page_images.append(pil_image)
      
   
    # Step 2: Refine with Gemini using all page images
    refined_text = await get_gemini_vision_review(page_images, raw_ocr_text)
 
    return refined_text
