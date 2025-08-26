from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dynamic Elements Manager"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./dynamic_elements.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Handle empty string
            if not v or v.strip() == "":
                return [
                    "http://localhost:3000",
                    "http://localhost:3001", 
                    "http://localhost:3002",
                    "http://localhost:3003",
                    "http://localhost:3004",
                    "http://localhost:3005",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:3001",
                    "http://127.0.0.1:3002",
                    "http://127.0.0.1:3003",
                    "http://127.0.0.1:3004",
                    "http://127.0.0.1:3005"
                ]
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []
    
    # File upload
    UPLOAD_FOLDER: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["txt", "pdf", "docx", "csv", "ppr-rx", "ppr-vx"]
    
    # Azure OpenAI Configuration (Primary)
    PING_FED_URL: str = os.getenv("PING_FED_URL", "")
    KGW_CLIENT_ID: str = os.getenv("KGW_CLIENT_ID", "")
    KGW_CLIENT_SECRET: str = os.getenv("KGW_CLIENT_SECRET", "")
    KGW_ENDPOINT: str = os.getenv("KGW_ENDPOINT", "")
    AOAI_API_VERSION: str = os.getenv("AOAI_API_VERSION", "")
    CHAT_MODEL_DEPLOYMENT_NAME: str = os.getenv("CHAT_MODEL_DEPLOYMENT_NAME", "")
    GPT_O3_MINI_DEPLOYMENT_NAME: str = os.getenv("GPT_O3_MINI_DEPLOYMENT_NAME", "")
    USE_O3_MINI: bool = os.getenv("USE_O3_MINI", "false").lower() == "true"
# Embeddings use standard model names, not deployment names
    
    # Legacy OpenAI Configuration (Backup)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    def assemble_allowed_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Handle empty string
            if not v or v.strip() == "":
                return ["txt", "pdf", "docx", "csv", "ppr-rx", "ppr-vx"]
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()