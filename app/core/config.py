import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "MarketYönetimi360 - Akıllı Yerel Market Yönetim Platformu"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_retail.db")
    ACADEMY_DOMAIN: str = "https://www.perakendekariyerakademisi.com"
    XPLUSCRM_DOMAIN: str = "https://app.xpluscrm.com"

settings = Settings()
