from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.schemas import (
    SkillVerificationPayload, TrainingAssignmentRequest,
    EmployeeSkillMatrixItem, TrainingImpactResponse
)
from app.services.academy_service import (
    verify_and_record_certification,
    assign_training_for_anomaly,
    get_store_skill_matrix,
    get_training_impact_report
)

router = APIRouter(prefix="/hr/skills", tags=["Perakende Kariyer Akademisi Entegrasyonu"])

@router.post("/skill-verification", summary="Akademi Sertifika ve Yetkinlik Doğrulama Webhook'u")
def skill_verification_api(
    payload: SkillVerificationPayload,
    db: Session = Depends(get_db)
):
    """
    Perakende Kariyer Akademisi'nde eğitimi ve sınavı başarıyla tamamlayan personelin
    sertifika ve yetkinlik güncellemesini Smart Retail 360'a işler.
    """
    try:
        cert_log = verify_and_record_certification(db, payload)
        return {
            "status": "success",
            "message": f"'{payload.employee_code}' personeli için '{payload.course_name}' sertifikası doğrulandı.",
            "certificate_id": cert_log.id,
            "exam_score": cert_log.exam_score,
            "passed": cert_log.passed
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/assign-training", summary="Operasyonel Sapma İçin Eğitim Atama")
def assign_training_api(
    req: TrainingAssignmentRequest,
    db: Session = Depends(get_db)
):
    """
    Mağazada oluşan fire, kasa kuyruğu veya denetim kusuru nedeniyle
    ilgili personele otomatik zorunlu eğitim atar ve aksiyon kartı oluşturur.
    """
    try:
        assignment = assign_training_for_anomaly(db, req)
        return {
            "status": "success",
            "message": f"Eğitim atandı: {assignment.course_name}",
            "event_id": assignment.event_id,
            "deadline_days": assignment.deadline_days,
            "assignment_id": assignment.id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/matrix", response_model=List[EmployeeSkillMatrixItem], summary="Şube Yetkinlik ve Beceri Matrisi")
def get_skill_matrix_api(
    store_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Mağaza bazında çalışanların departmanları, yetkinlik puanları,
    aktif eğitimleri ve sertifika sayılarını listeler.
    """
    return get_store_skill_matrix(db, store_id=store_id)

@router.get("/training-impact/{training_id}", response_model=TrainingImpactResponse, summary="Eğitim Sonrası KPI ve Finansal Geri Kazanım Raporu")
def get_training_impact_api(
    training_id: int,
    db: Session = Depends(get_db)
):
    """
    Tamamlanan eğitimin operasyonel fire ve KPI düzelmesine sağladığı
    parasal katkıyı ve hedef gerçekleşmesini ölçer (Closed-Loop LMS).
    """
    try:
        return get_training_impact_report(db, training_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
