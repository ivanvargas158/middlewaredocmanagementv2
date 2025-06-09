import os
from typing import List, Tuple
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from app.core.settings import get_settings
from app.utils.custom_exceptions import ValidationError
from app.services.mistral_ocr import process_mistral_ocr,validate_document,process_azurevision_ocr
from app.services.template_manager import register_template,match_template 
settings = get_settings()

def validate_file_type(filename: str, content_type: str):
    ext = os.path.splitext(filename)[1].lower()
    if content_type not in settings.allowed_mime_types:
        raise ValidationError(errors=f"Unsupported file type: {content_type}")
    if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]:
        raise ValidationError(errors=f"Unsupported file extension: {ext}")

def validate_file_size(file_bytes: bytes):
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_file_size:
        raise ValidationError(errors=f"File size exceeds {settings.max_file_size} MB limit.")
    
def split_pdf(file: bytes, tenantId:int)-> List[Tuple[str | None, float, bytes, str]]:
    list_pages: List[Tuple[str | None, float, bytes, str]] = []
    input_stream = BytesIO(file)#//sacar esto arribar que llegue solo el pdf_reader,para verificar arribar si el pdf tiene mas de un doc y ahver este metodo que retorne una lista de pages con su doc_type si existe
    pdf_reader = PdfReader(input_stream)
    doc_type_code:str|None = None
    score:float=0
    for i, page in enumerate(pdf_reader.pages):
        doc_type_code = None
        score = 0
        writer = PdfWriter()
        writer.add_page(page)
        # Save to BytesIO (in-memory)
        output_stream = BytesIO()
        writer.write(output_stream)
        output_bytes = output_stream.getvalue()

        ocrResult = process_azurevision_ocr(output_bytes)              
        ocr_text = ocrResult['ocr_text']
        doc_type_code,score = match_template(output_bytes,ocr_text,tenantId)
        list_pages.append((doc_type_code, score, output_bytes,ocr_text))
    return list_pages
        