import os
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator,fields,Field
from functools import lru_cache

class Settings(BaseSettings):

    enable_schema_enforcement: bool = True
    schema_admin_key: str = "your-secure-key"
    
    # --- API Endpoints ---
    mistral_ocr_endpoint: str = "https://api.mistral.ai/v1/ocr"

    schema_registry_url: str = "http://localhost:8001/schemas"
        
        
    azure_storage_endpoint_cargologik: str = "https://synapsevue.blob.core.windows.net/?sv=2024-11-04&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2026-01-01T03:53:32Z&st=2025-05-01T19:53:32Z&spr=https&sig=0vF4hBpmZG31qKSqOyNPtjqNbr9SfxXuQuwC48XIaR4%3D"
    azure_storage_endpoint_providence: str = "https://saprovidence01.blob.core.windows.net/?sv=2024-11-04&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2025-12-31T04:11:47Z&st=2025-05-29T20:11:47Z&spr=https&sig=CZ0FJZfUcKWtQ3iWq6TP%2BvudPU71t7vLXb%2FXXlKqtd4%3D"

    # --- Security Credentials ---
  
    schema_registry_token: Optional[str]= ""
    
    # --- Mistral

    mstral_api_Key: str = "VIJDVhgvEI7jBEFuwZFxXxyIHjTL7mA8"
    mistral_ocr_model: str = "mistral-ocr-latest"

    # --- OPEN AI -----
    Openai_Api_Key_ContextUser: str =  Field(validation_alias="Openai_API_Key")
    Openai_Base_Model_ContextUser: str = "gpt-4.1-mini"

    
    # -- Azure Vision
    
    azurevision_subscription_key:str = 'C0Dy78AegncXMpXGloMEcvFrQyeSPNNW5AGIqXLzJ1PcIgM9kRP2JQQJ99BAACYeBjFXJ3w3AAAFACOGYLc8'
    azurevision_endpoint:str = 'https://enhancevisionapi.cognitiveservices.azure.com/'

    # --- CosmosDB - Configuration ---
    cosmos_endpoint_cl: str = "https://synapsevue-cosmosdb.documents.azure.com:443/"
    cosmos_key_cl: str = "QJrtOoalYvYVRh8EfYjH90nS9v6hnRJffndCSCGJXgwUI30LvqVTFSKA5iExEpbN0ecnB7d92zOnACDb1Uqn1w=="
    cosmos_database_cl: str = "synapsevueAI"
    cosmos_container_contextual_recall_cl: str = "emailagent_memory"
    cosmos_container_doc_management_cl: str = "doc_management"

    cosmos_endpoint_providence: str = "https://providence-cosmosdb.documents.azure.com:443/"
    cosmos_key_providence: str = "VzollXNh63RGErEbnRzUgOjomOwYidK33EmkDTfnQy03a47Z4GLcCP7dued9zdocE7izvMkVTfxhACDblkyXBw=="
    cosmos_database_providence: str = "DataSync.cosmos"
    cosmos_container_providence: str = "FreightInvoice"


   
     # --- PostgreSQL - Configuration ---
    postgresql_host: str = "c-synapsevuedatabase.b6un2utbpmag4r.postgres.cosmos.azure.com"
    postgresql_db_name: str = "citus"
    postgresql_db_user: str = "citus"
    postgresql_db_pwd: str = "aV7Uccsj37TdmtA"


    # --- Security Settings ---
    cors_origins: List[str] = []

    rate_limit: int = 100

    enable_schema_enforcement: bool = True
    
    # --- Logging & Monitoring ---
    log_level: str = ""



        
    # --- Performance Tuning ---
    ocr_timeout: int = 30

    max_file_size: int = 50

    # Configurable settings
    max_file_size_mb:int = 10
    
    allowed_mime_types:set[str] = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/tiff"
    }
    
    # -- Tenants ---
    cargologik_tenant:str = "cargologik"
    providence_tenant:str = "providence"

    #Auth API Key

    
    api_key:str = "FEF85438-D360-4BC9-8265-7C0EC9F256C5"
    api_key_name:str = "x-api-key"

    # --- Validation Helpers ---
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["debug", "info", "warning", "error", "critical",""]
        if v.lower() not in valid_levels:
            raise ValueError(f"Invalid log level. Use: {', '.join(valid_levels)}")
        return v.lower()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        #secrets_dir = "/run/secrets"  # For Docker secrets
        
        # # Protect sensitive fields from logging
        # fields = {
        #     "AZURE_STORAGE_KEY": {"env": "AZURE_BLOB_KEY", "sensitive": True},
        #     "MISTRAL_API_KEY": {"env": "MISTRAL_OCR_KEY", "sensitive": True}
        # }

@lru_cache()
def get_settings() -> Settings:
    """Cache settings for fast access across application"""
    return Settings()

 