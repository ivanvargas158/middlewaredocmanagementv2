import asyncio
from pathlib import Path
from io import BytesIO
from docx import Document
from app.utils.soffice_utils import convert_with_soffice
async def extract_word_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()

    if ext == ".docx":
        # Directly extract from docx file bytes
        return await asyncio.to_thread(_extract_docx, file_bytes)

    elif ext == ".doc":
        # Convert .doc to .docx using LibreOffice, then extract text
        docx_bytes = await asyncio.to_thread(convert_with_soffice, file_bytes,".doc",".docx")
        return await asyncio.to_thread(_extract_docx, docx_bytes)

    else:
        raise ValueError(f"Unsupported Word format: {ext}")


def _extract_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Invalid or corrupted DOCX file: {e}")


 

 