import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "MarketYönetimi360 - Akıllı Yerel Market Yönetim Platformu"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_retail.db")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "marketyonetimi360_ultra_secure_jwt_secret_key_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 gün
    ACADEMY_DOMAIN: str = "https://www.perakendekariyerakademisi.com"
    XPLUSCRM_DOMAIN: str = "https://app.xpluscrm.com"

settings = Settings()
