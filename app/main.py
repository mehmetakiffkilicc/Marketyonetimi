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
from app.api.v1.auth import router as auth_router

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
app.include_router(auth_router, prefix=settings.API_V1_STR)

import os
from fastapi.staticfiles import StaticFiles
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/login", response_class=HTMLResponse)
def get_login_page():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "login.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/register", response_class=HTMLResponse)
def get_register_page():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "register.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/verify-email", response_class=HTMLResponse)
def get_verify_email_page():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "verify_email.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/tasarim-vitrini", response_class=HTMLResponse)
@app.get("/design-showcase", response_class=HTMLResponse)
def get_design_showcase():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "design_showcase.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

# Prototip route'ları
PROTOTYPES = {
    "hybrid": "prototype_hybrid.html",
    "obsidian": "prototype_obsidian.html",
    "nordic": "prototype_nordic.html",
    "titanium": "prototype_titanium.html",
    "midnight": "prototype_midnight.html",
    "ivory": "prototype_ivory.html",
}

@app.get("/prototype/{name}", response_class=HTMLResponse)
def get_prototype(name: str):
    if name not in PROTOTYPES:
        return HTMLResponse(content="<h1>Prototip bulunamadı</h1>", status_code=404)
    template_path = os.path.join(os.path.dirname(__file__), "templates", PROTOTYPES[name])
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/prototipler", response_class=HTMLResponse)
def get_prototype_gallery():
    html = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MarketYönetimi360 — Tasarım Prototipler</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#0a0a0f;color:#e4e4e7;min-height:100vh;padding:40px}
.header{text-align:center;margin-bottom:48px}
.header h1{font-size:32px;font-weight:800;letter-spacing:-0.5px;background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header p{color:#71717a;margin-top:8px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:24px;max-width:1200px;margin:0 auto}
.card{background:#18181b;border:1px solid #27272a;border-radius:16px;overflow:hidden;transition:all .3s ease;cursor:pointer;text-decoration:none;color:inherit}
.card:hover{border-color:#4f46e5;transform:translateY(-4px);box-shadow:0 20px 40px rgba(79,70,229,.15)}
.card-visual{height:180px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.card-visual .swatch{position:absolute;inset:0;opacity:.15}
.card-visual .label{font-size:48px;font-weight:800;opacity:.3;letter-spacing:-2px}
.card-body{padding:24px}
.card-body h3{font-size:18px;font-weight:700;margin-bottom:8px}
.card-body p{font-size:13px;color:#a1a1aa;line-height:1.6}
.tags{display:flex;gap:6px;margin-top:12px;flex-wrap:wrap}
.tag{font-size:10px;padding:4px 8px;border-radius:6px;background:#27272a;color:#a1a1aa;font-weight:600}
.btn-row{text-align:center;margin-top:40px}
.btn-row a{display:inline-block;padding:12px 32px;background:#4f46e5;color:white;border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;transition:background .2s}
.btn-row a:hover{background:#4338ca}
</style>
</head>
<body>
<div class="header">
<h1>MarketYönetimi360 Tasarım Prototipler</h1>
<p>5 farklı kurumsal tasarım konsepti — Her birini tıklayarak canlı deneyimleyin</p>
</div>
<div class="grid">

<a href="/prototype/hybrid" class="card" style="border-color: #3b82f6; box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);">
<div class="card-visual" style="background:linear-gradient(135deg,#1e3a5f,#0f2744)">
<div class="label" style="color:#60a5fa">HYB</div>
</div>
<div class="card-body">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
    <h3 style="color:#60a5fa;">Midnight + Titanium (Hibrit)</h3>
    <span style="background:#2563eb; color:white; font-size:10px; font-weight:800; padding:2px 8px; border-radius:10px;">YENİ</span>
</div>
<p>Titanium'un çelik lacivert degrade kenar çubuğu ve 6'lı kurumsal veri yoğunluğu, Midnight'ın Apple/Stripe zarafeti, 16px kavisleri ve beyaz tema zemininde birleşti.</p>
<div class="tags"><span class="tag" style="background:#1e3a5f; color:#93c5fd;">Steel Navy Sidebar</span><span class="tag">Açık Beyaz Zemin</span><span class="tag">6 KPI Grid</span><span class="tag">Canlı İlerleme Halkaları</span></div>
</div>
</a>

<a href="/prototype/obsidian" class="card">
<div class="card-visual" style="background:linear-gradient(135deg,#1a1a2e,#0d0d1a)">
<div class="label" style="color:#00d4aa">OBS</div>
</div>
<div class="card-body">
<h3>Obsidian Corporate</h3>
<p>Bloomberg Terminal + SAP Fiori ilhamıyla koyu kurumsal tema. Glass-morphism kartlar, teal aksanlar, veri yoğun komuta merkezi.</p>
<div class="tags"><span class="tag">Koyu Tema</span><span class="tag">Glass-morphism</span><span class="tag">Veri Yoğun</span></div>
</div>
</a>

<a href="/prototype/nordic" class="card">
<div class="card-visual" style="background:linear-gradient(135deg,#fafaf9,#eef2ff)">
<div class="label" style="color:#4f46e5">NRD</div>
</div>
<div class="card-body">
<h3>Nordic Precision</h3>
<p>Linear.app + Vercel ilhamıyla İskandinav minimalizmi. Temiz beyaz yüzeyler, indigo aksanlar, İsviçre tasarım prensipleri.</p>
<div class="tags"><span class="tag">Açık Tema</span><span class="tag">Minimalist</span><span class="tag">Swiss Design</span></div>
</div>
</a>

<a href="/prototype/titanium" class="card">
<div class="card-visual" style="background:linear-gradient(135deg,#1e3a5f,#0f2744)">
<div class="label" style="color:#3b82f6">TTN</div>
</div>
<div class="card-body">
<h3>Titanium Enterprise</h3>
<p>Salesforce + Microsoft Fabric ilhamıyla kurumsal mavi-gri tema. CFO'nun günlük kullanacağı güven veren arayüz.</p>
<div class="tags"><span class="tag">Kurumsal</span><span class="tag">Steel Blue</span><span class="tag">Enterprise-Grade</span></div>
</div>
</a>

<a href="/prototype/midnight" class="card">
<div class="card-visual" style="background:linear-gradient(135deg,#09090b,#1e1b4b)">
<div class="label" style="color:#7c3aed">MID</div>
</div>
<div class="card-body">
<h3>Midnight Executive</h3>
<p>Apple + Stripe Dashboard ilhamıyla ultra-premium koyu mod. Violet aksanlar, progress ring'ler, lüks otomobil kokpiti hissi.</p>
<div class="tags"><span class="tag">Ultra-Dark</span><span class="tag">Premium</span><span class="tag">Apple-Inspired</span></div>
</div>
</a>

<a href="/prototype/ivory" class="card">
<div class="card-visual" style="background:linear-gradient(135deg,#faf8f5,#f5f0e8)">
<div class="label" style="color:#14532d">IVR</div>
</div>
<div class="card-body">
<h3>Ivory Institutional</h3>
<p>J.P. Morgan + McKinsey ilhamıyla bankacılık estetiği. Serif fontlar, altın aksanlar, yönetim kurulu raporlama kalitesi.</p>
<div class="tags"><span class="tag">Institutional</span><span class="tag">Serif</span><span class="tag">Board-Level</span></div>
</div>
</a>

</div>
<div class="btn-row"><a href="/dashboard">← Mevcut Dashboard'a Dön</a></div>
</body>
</html>"""
    return HTMLResponse(content=html)

