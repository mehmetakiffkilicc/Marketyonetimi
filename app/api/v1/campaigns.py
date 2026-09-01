from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.schemas import CampaignReportItem
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Kampanya Yönetimi & Takvim"])

@router.get("", response_model=List[CampaignReportItem])
def list_campaigns(
    category_id: Optional[int] = Query(None, description="Kategori filtresi"),
    supplier_id: Optional[int] = Query(None, description="Üretici / Marka filtresi"),
    db: Session = Depends(get_db)
):
    """
    Tüm geçmiş, aktif ve planlanan kampanyaları listeler.
    Kategori ve Marka bazında filtrelemeyi destekler.
    Ürün bazında raf fiyatı, aktivite fiyatı, hedef satış ve uygulama kanalını raporlar.
    """
    return CampaignService.get_campaign_reports(db, category_id=category_id, supplier_id=supplier_id)

from app.schemas.schemas import CampaignReportItem, SingleProductCampaignCreateRequest

@router.post("")
def create_single_campaign(
    req: SingleProductCampaignCreateRequest,
    db: Session = Depends(get_db)
):
    """Tekil bir ürün için bağımsız kampanya planlar ve onaylar."""
    try:
        return CampaignService.create_single_product_campaign(db, req)
    except ValueError as e:
        return {"status": "error", "message": str(e)}

@router.get("/export")
def export_campaigns(
    campaign_id: Optional[int] = Query(None, description="Opsiyonel tekil kampanya ID"),
    db: Session = Depends(get_db)
):
    """
    Kampanya planlama verilerini, ürün barkodlarını, raf ve aktivite fiyatlarını, 
    hedef satış adetlerini ve dijital kart/raf ayrımını doğrudan Excel (.xlsx) formatında indirir.
    """
    excel_stream = CampaignService.export_campaigns_to_excel(db, campaign_id=campaign_id)
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=SmartRetail_Kampanya_Plani_2026.xlsx"
        }
    )
