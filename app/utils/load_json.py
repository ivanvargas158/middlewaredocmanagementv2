import json
from app.schemas.general_enum import DocumentType
from pathlib import Path

schema_files = {
    DocumentType.commercial_invoice: "commercial_invoice.json",
    DocumentType.master_bill_of_lading: "master_bill_of_lading.json",
    DocumentType.one_ocean_master_bill_of_lading: "one_ocean_master_bill_of_lading.json",
    DocumentType.packing_list_swift: "packing_list_swift.json",
    DocumentType.packing_list_minerva: "packing_list_minerva.json",
    DocumentType.argentina_health_certificate: "health_certificate_argentina.json",
    DocumentType.brasil_health_certificate: "health_certificate_brasil.json",
    DocumentType.certificate_of_analysis: "certificate_of_analysis.json",
    DocumentType.certificate_of_origin: "certificate_of_origin.json",
    DocumentType.nop_import_certificate: "nop_import_certificate.json",
    DocumentType.brasil_isf: "brasil_isf.json",
    DocumentType.brasil_certificate_of_analysis: "brasil_certificate_of_analysis.json",
    DocumentType.brasil_master_bill_of_lading: "brasil_master_bill_of_lading.json",
    DocumentType.brasil_health_certificate: "brasil_health_certificate.json",
    DocumentType.brasil_commercial_invoice: "brasil_commercial_invoice.json",
    DocumentType.brasil_packing_list: "brasil_packing_list.json",
    DocumentType.brasil_certificate_of_origin: "brasil_certificate_of_origin.json",
    DocumentType.brasil_master: "brasil_master.json",
    DocumentType.abf_freight_invoice: "abf_invoice.json"
}

# Load all schemas into a dictionary at startup
schema_dir = Path.cwd() / "app/schemas/json_schemas"
# Set up paths
base_dir = Path.cwd() / "app/schemas/json_schemas"
# Include main dir + specific subdirs
directories_to_scan = [base_dir, base_dir / "brasil"]

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
