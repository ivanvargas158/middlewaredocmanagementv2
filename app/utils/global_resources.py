
from app.services.office.extract_word_service import extract_word_text
from app.services.office.extract_excel_service import extract_tabular_text

mime_type_to_extractor = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": extract_tabular_text,  # Excel
    "application/vnd.ms-excel": extract_tabular_text,  # Excel
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": extract_word_text,  # Word
    "application/msword": extract_word_text  # Word
}
