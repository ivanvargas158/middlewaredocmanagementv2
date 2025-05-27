import json
from app.schemas.general_enum import DocumentType
from pathlib import Path

schema_files = {
    DocumentType.commercial_invoice: "commercial_invoice.json",
    DocumentType.master_bill_of_lading: "master_bill_of_lading.json",
    DocumentType.one_ocean_master_bill_of_lading: "one_ocean_master_bill_of_lading.json",
    DocumentType.packing_list_swift: "packing_list_swift.json",
    DocumentType.packing_list_minerva: "packing_list_minerva.json",
    DocumentType.health_certificate_argentina: "health_certificate_argentina.json",
    DocumentType.health_certificate_brasil: "health_certificate_brasil.json",
    DocumentType.certificate_of_analysis: "certificate_of_analysis.json",
    DocumentType.certificate_of_origin: "certificate_of_origin.json",
    DocumentType.nop_import_certificate: "nop_import_certificate.json",
    DocumentType.abf_freight_invoice: "abf_invoice.json"
}

# Load all schemas into a dictionary at startup
schema_dir = Path.cwd() / "app/schemas/json_schemas"
loaded_schemas = {}

for doc_type, file_name in schema_files.items():
    file_path = schema_dir / file_name
    try:
        with open(file_path, "r") as file:
            loaded_schemas[doc_type] = json.load(file)
    except FileNotFoundError:
        raise Exception(f"Schema file not found: {file_path}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON in schema file: {file_path}")

def get_json_schema(doc_type: DocumentType) -> str:
    return loaded_schemas.get(doc_type, "")
