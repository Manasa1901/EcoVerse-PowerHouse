from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings(BaseModel):
    # watsonx
    watsonx_api_key: str = Field(alias="WATSONX_API_KEY")
    watsonx_url: str = Field(alias="WATSONX_URL")
    watsonx_project_id: Optional[str] = Field(default=None, alias="WATSONX_PROJECT_ID")
    watsonx_space_id: Optional[str] = Field(default=None, alias="WATSONX_SPACE_ID")

    # TTS
    tts_api_key: str = Field(alias="TTS_API_KEY")
    tts_url: str = Field(alias="TTS_URL")

    # COS (optional)
    cos_endpoint: Optional[str] = Field(default=None, alias="COS_ENDPOINT")
    cos_api_key: Optional[str] = Field(default=None, alias="COS_API_KEY")
    cos_instance_crn: Optional[str] = Field(default=None, alias="COS_INSTANCE_CRN")
    cos_bucket: Optional[str] = Field(default=None, alias="COS_BUCKET")
    cos_region: Optional[str] = Field(default=None, alias="COS_REGION")

    cors_origins: List[str] = Field(default_factory=list, alias="CORS_ORIGINS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


def load_settings() -> Settings:
    origins_raw = os.getenv("CORS_ORIGINS", "")
    origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
    
    data = {
        "WATSONX_API_KEY": os.getenv("WATSONX_API_KEY"),
        "WATSONX_URL": os.getenv("WATSONX_URL"),
        "WATSONX_PROJECT_ID": os.getenv("WATSONX_PROJECT_ID"),
        "WATSONX_SPACE_ID": os.getenv("WATSONX_SPACE_ID"),
        "TTS_API_KEY": os.getenv("TTS_API_KEY"),
        "TTS_URL": os.getenv("TTS_URL"),
        "COS_ENDPOINT": os.getenv("COS_ENDPOINT"),
        "COS_API_KEY": os.getenv("COS_API_KEY"),
        "COS_INSTANCE_CRN": os.getenv("COS_INSTANCE_CRN"),
        "COS_BUCKET": os.getenv("COS_BUCKET"),
        "COS_REGION": os.getenv("COS_REGION"),
        "CORS_ORIGINS": origins,
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }

    return Settings.model_validate(data)
