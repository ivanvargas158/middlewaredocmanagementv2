import asyncio
from pathlib import Path
from io import BytesIO
from docx import Document
import tempfile
import subprocess
import os

async def extract_word_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()

    if ext == ".docx":
        # Directly extract from docx file bytes
        return await asyncio.to_thread(_extract_docx, file_bytes)

    elif ext == ".doc":
        # Convert .doc to .docx using LibreOffice, then extract text
        docx_bytes = await asyncio.to_thread(convert_doc_to_docx, file_bytes)
        return await asyncio.to_thread(_extract_docx, docx_bytes)

    else:
        raise ValueError(f"Unsupported Word format: {ext}")


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    try:
        doc = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Invalid or corrupted DOCX file: {e}")


def convert_doc_to_docx(doc_bytes: bytes,timeout: int = 20) -> bytes:

    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "input.doc")
        docx_path = os.path.join(tmpdir, "input.docx")

        # Save input .doc bytes
        with open(doc_path, "wb") as f:
            f.write(doc_bytes)
        # r"C:\Program Files\LibreOffice\program\soffice.exe", 
        # Run LibreOffice headless to convert .doc to .docx
        cmd = [
            r"soffice",         # LibreOffice executable, e.g., /usr/bin/soffice
            "--headless",      # Run without UI
            "--convert-to", "docx",  # Output format
            "--outdir", tmpdir,       # Output folder
            doc_path
        ]

        try:
            completed = subprocess.run(
                cmd, check=True, capture_output=True,timeout=timeout
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(
                f"LibreOffice conversion timed out after {timeout} seconds."
            )
        except subprocess.CalledProcessError as e:
            # Raise error with LibreOffice output for debugging
            err_msg = e.stderr.decode(errors="ignore")
            raise RuntimeError(f"LibreOffice conversion failed: {err_msg}")

        # Verify output .docx exists
        if not os.path.exists(docx_path):
            raise FileNotFoundError("Conversion failed: output .docx file not found")

        # Read the converted .docx bytes and return
        with open(docx_path, "rb") as f:
            return f.read()

 