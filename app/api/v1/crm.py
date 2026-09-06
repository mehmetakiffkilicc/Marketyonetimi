from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import (
    CRMSimulationRequest, CRMSimulationResponse,
    CRMCampaignFeedbackPayload, CRMCampaignInsightItem
)
from app.services.crm_service import (
    simulate_overstock_liquidation,
    record_crm_campaign_feedback,
    get_crm_campaign_insights
)

router = APIRouter(prefix="/crm", tags=["XPlusCRM Entegrasyonu"])

@router.post("/simulate-liquidation", response_model=CRMSimulationResponse, summary="Fazla Stok CRM Tasfiye Simülasyonu")
def simulate_liquidation_api(
    req: CRMSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Belirli bir mağazada fazla stoğu bulunan ürün için XPlusCRM hedef kitle,
    indirim ve sepet ciro simülasyonu yapar.
    """
    try:
        return simulate_overstock_liquidation(db, req.store_id, req.product_id, req.max_discount_pct)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/campaign-feedback", summary="XPlusCRM Kampanya Geri Dönüş Webhook'u")
def crm_campaign_feedback_api(
    payload: CRMCampaignFeedbackPayload,
    db: Session = Depends(get_db)
):
    """
    XPlusCRM tarafından yürütülen hedeflenmiş kampanyanın fiili dönüşüm,
    satış adedi ve sepet ciro sonuçlarını Smart Retail 360'a kaydeder.
    """
    feedback = record_crm_campaign_feedback(db, payload)
    return {
        "status": "success",
        "message": f"Kampanya #{feedback.campaign_id} geri bildirimi başarıyla işlendi.",
        "feedback_id": feedback.id,
        "units_sold": feedback.units_sold,
        "total_revenue_generated_try": feedback.total_revenue_generated_try
    }

@router.get("/campaign-insights", response_model=List[CRMCampaignInsightItem], summary="CRM Kampanya Performans & İçgörü Listesi")
def get_campaign_insights_api(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    XPlusCRM üzerinden tamamlanan tüm kişiselleştirilmiş kampanyaların
    performans ve finansal geri kazanım geçmişini listeler.
    """
    return get_crm_campaign_insights(db, limit=limit)
