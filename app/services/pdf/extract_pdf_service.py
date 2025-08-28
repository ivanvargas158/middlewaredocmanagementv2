import io
import PyPDF2
 

def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_stream = io.BytesIO(file_content)
        reader = PyPDF2.PdfReader(pdf_stream)
        texts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(texts)

    except Exception as e: 
        raise ValueError(f"Invalid or corrupted PDF file: {e}")
