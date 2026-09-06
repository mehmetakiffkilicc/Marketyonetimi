from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.schemas import (
    ActionCardCreate, ActionCardResolveRequest, ActionCardOut,
    TriggerAuditRunResponse
)
from app.services.trigger_service import (
    create_action_card, list_action_cards, resolve_action_card,
    run_comprehensive_audit
)

router = APIRouter(prefix="/triggers", tags=["Tetikleyiciler & Aksiyon Motoru"])

@router.post("/run-audit", response_model=TriggerAuditRunResponse, summary="Sistem Geneli Anomali Denetimi ve Tetikleyici Başlatma")
def run_audit_api(
    db: Session = Depends(get_db)
):
    """
    Tüm mağaza ve ürünlerde fazla stok, fire sapması ve denetim kusurlarını tarar;
    XPlusCRM ve Perakende Kariyer Akademisi tetikleyicilerini çalıştırıp
    otomatik aksiyon kartları oluşturur.
    """
    return run_comprehensive_audit(db)

@router.get("/action-cards", response_model=List[ActionCardOut], summary="Açık Aksiyon Kartları Listesi")
def get_action_cards_api(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source_module: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Şirket genelinde açılmış tüm aksiyon kartlarını durum, öncelik ve kaynak modüle göre listeler.
    """
    return list_action_cards(db, status=status, priority=priority, source_module=source_module, limit=limit)

@router.post("/action-cards", response_model=ActionCardOut, summary="Yeni Aksiyon Kartı Oluştur")
def create_action_card_api(
    data: ActionCardCreate,
    db: Session = Depends(get_db)
):
    """
    Manuel veya sistem kaynaklı yeni bir aksiyon ve görev kartı açar.
    """
    card = create_action_card(db, data)
    return ActionCardOut.model_validate(card)

@router.post("/action-cards/{card_id}/resolve", response_model=ActionCardOut, summary="Aksiyon Kartını Çözümle & Kapat")
def resolve_action_card_api(
    card_id: int,
    data: ActionCardResolveRequest,
    db: Session = Depends(get_db)
):
    """
    Açık olan bir aksiyon kartını kanıt açıklaması ve geri kazanılan parasal tutar ile kapatır.
    """
    try:
        return resolve_action_card(db, card_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
