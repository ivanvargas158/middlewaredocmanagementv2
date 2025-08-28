
import re
from app.services.office.extract_word_service import extract_word_text
from app.services.office.extract_excel_service import extract_tabular_text
from app.services.pdf.extract_pdf_service import extract_text_from_pdf

mime_type_to_extractor = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": extract_tabular_text,  # Excel
    "application/vnd.ms-excel": extract_tabular_text,  # Excel
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": extract_word_text,  # Word
    "application/msword": extract_word_text,  # Word
    "application/pdf": extract_text_from_pdf
}

def remove_yaml_block(text: str) -> str: 
    return re.sub(r'---\s*```yaml.*?```', '', text, flags=re.DOTALL).strip()