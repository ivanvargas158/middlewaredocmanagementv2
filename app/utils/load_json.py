import json
from app.schemas.general_enum import DocumentType
from pathlib import Path

schema_files = {
    DocumentType.brasil_isf: "brasil_isf.json",
    DocumentType.brasil_certificate_of_analysis: "brasil_certificate_of_analysis.json",
    DocumentType.brasil_master_bill_of_lading: "brasil_master_bill_of_lading.json",
    DocumentType.brasil_health_certificate: "brasil_health_certificate.json",
    DocumentType.brasil_commercial_invoice: "brasil_commercial_invoice.json",
    DocumentType.brasil_packing_list: "brasil_packing_list.json",
    DocumentType.brasil_certificate_of_origin: "brasil_certificate_of_origin.json",
    DocumentType.brasil_master: "brasil_master.json",  
    DocumentType.ef_pdf_invoice_1: "ef_pdf_invoice_1.json",
    DocumentType.ef_xls_type_4: "ef_xls_type_4.json",
    DocumentType.ef_xls_type_isf_3: "ef_xls_type_isf_3.json",
    DocumentType.ef_xlsx_type_ci_1: "ef_xlsx_type_ci_1.json",
    DocumentType.ef_xlsx_type_isf_2: "ef_xlsx_type_isf_2.json",
    DocumentType.ef_doc_type_ci_1: "ef_doc_type_ci_1.json",
}

# Load all schemas into a dictionary at startup
schema_dir = Path.cwd() / "app/schemas/json_schemas"
# Set up paths
base_dir = Path.cwd() / "app/schemas/json_schemas"
# Include main dir + specific subdirs
directories_to_scan = [base_dir, base_dir / "brasil",base_dir / "exFreight"]

loaded_schemas = {}

# Loop through all directories and load JSON files
for directory in directories_to_scan:
    for file_path in directory.glob("*.json"):
        file_name = file_path.name
        doc_type = next((k for k, v in schema_files.items() if v == file_name), None)
        if doc_type:
            try:
                with open(file_path, "r") as file:
                    loaded_schemas[doc_type] = json.load(file)
            except FileNotFoundError:
                raise Exception(f"Schema file not found: {file_path}")
            except json.JSONDecodeError:
                raise Exception(f"Invalid JSON in schema file: {file_path}")


def get_json_schema(doc_type: DocumentType) -> str:
    return loaded_schemas.get(doc_type, "")
