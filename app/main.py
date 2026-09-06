from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database
from app.api.v1.purchasing import router as purchasing_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.master import router as master_router
from app.api.v1.stores import router as stores_router
from app.api.v1.crm import router as crm_router
from app.api.v1.academy import router as academy_router
from app.api.v1.triggers import router as triggers_router

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

# Veritabanını tohumla
with SessionLocal() as db_session:
    seed_database(db_session)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="marketyönetimi360 - Yerel Market Zincirleri için Uçtan Uca Perakende İşletim Sistemi, CRM, Akademi ve Tetikleyici API'si",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Router'larını bağla
app.include_router(purchasing_router, prefix=settings.API_V1_STR)
app.include_router(suppliers_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(campaigns_router, prefix=settings.API_V1_STR)
app.include_router(master_router, prefix=settings.API_V1_STR)
app.include_router(stores_router, prefix=settings.API_V1_STR)
app.include_router(crm_router, prefix=settings.API_V1_STR)
app.include_router(academy_router, prefix=settings.API_V1_STR)
app.include_router(triggers_router, prefix=settings.API_V1_STR)

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    import os
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

