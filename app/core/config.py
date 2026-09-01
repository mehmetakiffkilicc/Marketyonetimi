import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Smart Retail AI - Akıllı Yerel Market Yönetim Platformu"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_retail.db")

settings = Settings()
