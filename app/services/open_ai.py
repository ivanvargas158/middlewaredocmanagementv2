import json
from openai import OpenAI
from app.core.settings import get_settings
from app.schemas.general_enum import DocumentType
from app.utils.load_json import get_json_schema
from app.utils.custom_exceptions import ValidationError

settings = get_settings()

client = OpenAI(
        api_key = settings.Openai_Api_Key_ContextUser
    )

def extract_keywords_openAI(doc_type: DocumentType,doc_text:str):
    
    schema_mapping_data:str = get_json_schema(doc_type)
    if schema_mapping_data=="":
        raise ValidationError(errors=f"Invalid document type(schema json) : {doc_type}")
     
    try:  

        openai_prompt = """You are an advanced document understanding agent, optimized for shipping and logistics workflows and designed to work in tandem with the Mistral OCR API.
        Your responsibilities are:
        Parse the Mistral OCR output (provided in markdown format), which includes field names and extracted values.
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
        Mistral OCR Markdown Output
        {ocr_markdown}
        Output Format Example
        {{"bol_number":"12345","shipper_name":"ACME Corp","consignee_name":null}}
        Instructions Recap:
        Only use schema field names as JSON keys.
        Do not include any fields not listed in the schema mapping.
        Do not invent or hallucinate values.
        Ensure the JSON is valid and minified.
        Only return the final JSON output—no extra text."""

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

    except json.JSONDecodeError as e:
        raise ValidationError(errors=f"Error: Failed to parse JSON from LLM response for memory extraction: {e}")
    except Exception as e:
        raise ValidationError(errors=f"Error during memory extraction: {e}")
    


def extract_keywords_openAI_freight_invoice(doc_type: DocumentType,doc_text:str):
    
    schema_mapping_data:str = get_json_schema(doc_type)
    if schema_mapping_data=="":
        raise ValidationError(errors=f"Invalid document type(schema json) : {doc_type}")
     
    try:  
        openai_prompt = f"""
            You are an expert in freight invoice parsing. Given the following OCR output, extract all relevant fields to strict JSON using this schema:

            {schema_mapping_data}

            Special field notes:
            - dimensions: {{ length_in, width_in, height_in }}  
            - accessorials: [
                {{
                name: (string),
                in_rate: (true if "IN RATE" or similar appears, else false),
                charge: (float, if a dollar amount is listed for the accessorial, else null)
                }}
            ]
            - reasoning_notes (brief: especially explain if accessorials were included in rate or line item charged)        

            **Accessorials Extraction Rule:**  
            Return all accessorials found. For each, set 'in_rate' to true if the accessorial is shown as 'IN RATE' (included in rate, not extra-charged); set 'charge' if there is a separate dollar amount. If the accessorial was requested by the customer but included due to contract, still list it with 'in_rate': true.

            Respond in strict JSON. Example:
            {{
            "accessorials": [
                {{ "name": "ARRIVAL NOTICE", "in_rate": true, "charge": null }},
                {{ "name": "FUEL SURCHARGE", "in_rate": true, "charge": null }}
            ],
            ...
            }}

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

    except json.JSONDecodeError as e:
        raise ValidationError(errors=f"Error: Failed to parse JSON from LLM response for memory extraction: {e}")
    except Exception as e:
        raise ValidationError(errors=f"Error during memory extraction: {e}")
    