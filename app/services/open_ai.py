import json
from openai import OpenAI
from app.core.settings import get_settings
from app.schemas.general_enum import DocumentType
from app.utils.load_json import get_json_schema
from fastapi import HTTPException

settings = get_settings()

client = OpenAI(
        api_key = settings.Openai_Api_Key_ContextUser,
    )

def extract_keywords_openAI(doc_type: DocumentType,doc_text:str):
    
    schema_mapping_data:str = get_json_schema(doc_type)
    if schema_mapping_data=="":
        raise HTTPException(status_code=500, detail=f"Invalid document type(schema json) : {doc_type}")   

    openai_prompt = """You are an advanced document understanding agent, optimized for shipping and logistics workflows and designed to work in tandem with the OCR API.
    Your responsibilities are:
    Parse the OCR output (provided in markdown format), which includes field names and extracted values.
    Precisely map each extracted field to its corresponding internal schema field using the provided schema mapping table.
    For each schema field, output a JSON object with:
    The internal schema field name as the key.
    If a field is missing or ambiguous in the OCR data, set: null
    Strictly adhere to the schema mapping: Only include fields listed in the schema mapping table. Do not infer, invent, or hallucinate any values or fields.
    Output requirements:
    The result must be a valid, minified JSON object (no line breaks or extra spaces).
    Do not include any commentary, explanation, or formatting outside of the JSON.
    Schema Mapping Table
    {schema_mapping}
    OCR Markdown Output
    {ocr_markdown}
    Instructions Recap:
    Only use schema field names as JSON keys.
    Do not include any fields not listed in the schema mapping.
    Do not invent or hallucinate values.
    Ensure the JSON is valid and minified.
    Only return the final JSON output—no extra text.

    rules:
     - the field 'packagesInfo' exist in schema mapping  , Each entry begins with "[amount] [packageType]" and includes "N. W." followed by the weight.
    
    Use this example if the fields exist in schema mapping:

        Example 1:
        OCR Markdown:
        shipper_name: FORTUNCERES S.A  
        shipper_address: ST PROJETADA, KM 4, LINHA 119,S/N CORUMBIARA - CHUPINGUAIA  
        shipper_location: RONDONIA - BRAZIL  
        shipper_country_code: BR,get the country code from  shipper_location
        consignee_name: MINERVA MEATS USA INC  
        consignee_address: 2400 E COMMERCIAL BLVD. SUITE 711  
        consignee_location: FORT LAUDERDALE, FL 33308 U.S.A  
        consignee_country_code: US, get the country code from consignee_location
        internalReference: 123456789, this is the shipper's CNPJ
        packagesInfo: packageType: Cartons, amount: 100, weight: 5000, weightMetric: KG, hazardousMaterials: No
    """

    openai_prompt = openai_prompt.format(schema_mapping=schema_mapping_data, ocr_markdown=doc_text)

    response = client.chat.completions.create(
        model = settings.Openai_Base_Model_ContextUser,
        messages = [
            {"role": "user", "content": openai_prompt},
        ],
        temperature = 0.0,
        response_format={ "type": "json_object" }

    ) 

    content = response.choices[0].message.content

    response_data = json.loads(str(content))        

    return response_data

    
def extract_keywords_openAI_freight_invoice(doc_type: DocumentType,doc_text:str):
    
    schema_mapping_data:str = get_json_schema(doc_type)
    if schema_mapping_data=="":
        raise HTTPException(status_code=500, detail=f"Invalid document type(schema json) : {doc_type}")     
 
    openai_prompt = f"""
        You are an expert in freight invoice parsing. Given the following OCR output, extract all relevant fields to strict JSON using this schema:

        {schema_mapping_data}

        ### Special Parsing Rules and Notes ### 

        1. **Accessorials Extraction Rule:**  

            - accessorials: [
                {{
                name: (string),
                code: (string),
                in_rate: (true if "IN RATE" or similar appears, else false),
                charge: (float, if a dollar amount is listed for the accessorial, else null)
                }}
            ]

            - reasoning_notes (brief: especially explain if accessorials were included in rate or line item charged)
            
            - Return all accessorials found. For each, set 'in_rate' to true if the accessorial is shown as 'IN RATE' (included in rate, not extra-charged); set 'charge' if there is a separate dollar amount. If the accessorial was requested by the customer but included due to contract, still list it with 'in_rate': true.

            - Respond in strict JSON. Example:
                {{
                "accessorials": [
                    {{ "name": "ARRIVAL NOTICE","code":"ARR", "in_rate": true, "charge": null }},
                    {{ "name": "FUEL SURCHARGE","code":"FSC", "in_rate": true, "charge": null }}
                    {{ "name": "SPECIAL HANDLING SERVICES - LUMPER","code":"SHDL", "in_rate": false, "charge": 60,"description": }}
                ],
            
            }}

        2. **NMFC Sub Extraction Rule:**  
            - Extract the NMFC sub number from the following NMFC codes. The sub number is the two-digit number that follows the dash (-) in the code. Ignore any letters that come after the sub number.
                Examples:
                    NMFC 067050-01V → Sub: 01
                    NMFC 073150-03 → Sub: 03 

        3. **Dimensions Extraction Rule:**  
            
            - For each freight line item, scan all parts of the invoice (including body, tables, footnotes, and unstructured text) for mentions of:
                - Dimensions: length, width, and height — in inches (e.g. "48x40x60", "L48 W40 H60", or "48in L x 40in W x 60in H").
                - Units may be abbreviated or missing — infer "inches" unless otherwise stated.
                - Add the class, nmfc_code, nmfc_sub and package for each dimension
                    - package, is the type of package. For example 2 PLT, the package is PLT.

            - Respond in strict JSON. Example:
                {{
                "dimensions": [
                    {{ "qty": 1,"length_in":48, "width_in": 40, "height_in": 41,"class":"70","nmfc_code":"067050","nmfc_sub":"02","packaging":"PLT" }},
                    {{ "qty": 1,"length_in":48, "width_in": 40, "height_in": 43,"class":"70","nmfc_code":"067050","nmfc_sub":"02","packaging":"SKD" }},
                ],            
                }}   
        4. **Piece Extraction Rule:**

            - piece_count:

                - Extract numeric values that appear before units such as PLT, SKD, or similar (e.g., "1 PLT", "3 PLT", "1 SKD").
                - Only return the numeric portion (e.g., from "3 PLT" → return 3).
                - Return a single integer.

            - total_piece_count:

                - Locate the section of OCR text where the phrase "Total Pieces" appears.
                - Extract the number found directly next to or beneath the phrase "Total Pieces".
                  - **Exclude any values associated with misleading labels like "TOTAL IND PIECES", "TOTAL INDIVIDUAL PIECES", or similar variations — these are not valid indicators for total_pieces.**
                - Only use values where the label clearly and exactly states "Total Pieces" without extra qualifiers.
                - Return a single integer.
        
        Special Field Mapping Notes:

            - Always assign values **to the right of the label**, not the label text itself.
            - If you see a labeled field in the format:
                    [LABEL]: [VALUE]

            - The label (e.g. "P.O. Number") is the key.
            - The value (e.g. "4162512") to the right of the colon is what should be extracted.

            - For example:
                - "P.O. Number: 4162512" → `"po_number": "4162512"`
                - "Freight Bill No.: 007058071" → `"pro_number": "007058071"`

            - Do not mistakenly extract the label text itself (e.g., "P.O. Number") as the value.             

        Here is the OCR text:
        \"\"\"
        {doc_text}
        \"\"\"
        """


    response = client.chat.completions.create(
        model = settings.Openai_Base_Model_ContextUser,
        messages = [
            {"role": "user", "content": openai_prompt},
        ],
        temperature = 0.0,
        response_format={ "type": "json_object" }

    ) 

    content = response.choices[0].message.content

    response_data = json.loads(str(content))        

    return response_data
 
    