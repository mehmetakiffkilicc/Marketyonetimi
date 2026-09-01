from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import FinancialBurdenResponse, StockoutAnalysisResponse, ExecutiveDashboardSummary
from app.services.financial_burden_service import FinancialBurdenService
from app.services.stockout_service import StockoutService
from app.services.executive_service import ExecutiveService

router = APIRouter(prefix="/analytics", tags=["Finansal Analiz & Karar Destek"])

from typing import Optional

@router.get("/executive-summary", response_model=ExecutiveDashboardSummary)
def get_executive_summary(
    store_id: Optional[int] = None,
    buyer_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Patron & Genel Yönetim Masası (Executive Cockpit):
    - Zincir geneli veya seçilen Mağaza / Satın Alma Müdürü / Üretici Firma bazında konsolide ciro, maliyet, brüt kâr, GMROI ve stok sermayesi
    - Şube bazlı ciro, kârlılık, stok yükü ve kritik stok metrikleri
    - Kategori bazlı ciro ve GMROI dağılımı
    - Erken uyarılar: En çok ciro kaybettiren yok satanlar, atıl stoklar, yaklaşan vadeli ödemeler ve yıldız üreticiler
    """
    return ExecutiveService.get_executive_summary(
        db,
        store_id=store_id,
        buyer_id=buyer_id,
        supplier_id=supplier_id,
        category_id=category_id
    )

@router.get("/financial-burden", response_model=FinancialBurdenResponse)
def get_financial_burden(db: Session = Depends(get_db)):
    """
    Stokların Finansal Yükü & Bağlı Sermaye Analizi:
    - Kategori bazlı stok maliyeti, payı ve devir gün sayısı
    - Satın almacı bazlı bağlı sermaye, bütçe kullanım oranı ve atıl stok (>45 gün) tutarı
    - Üretici bazlı bağlı sermaye ve Vade Açığı (Yeter Gün - Vade) ile nakit kanaması riski
    """
    return FinancialBurdenService.get_financial_burden(db)

@router.get("/stockouts", response_model=StockoutAnalysisResponse)
def get_stockouts_and_gaps(db: Session = Depends(get_db)):
    """
    İkmal Uyuşmazlığı & Yok Satanlar Raporu:
    - Ana depoda bolca varken mağazalarda 0 stoğa inmiş ürünler (Otomatik transfer önerisi)
    - Yok satan ürünler, stoksuz kalınan günler ve tahmini ciro kaybı tutarları
    - Kök neden analizi (Depo ikmal gecikmesi vs Tedarikçi sipariş eksikliği)
    """
    return StockoutService.get_stockout_analysis(db)
