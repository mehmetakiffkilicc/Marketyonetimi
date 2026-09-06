import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import (
    Employee, EmployeeCompetency, TrainingAssignment, CertificationLog,
    Store, ActionCard, ActionCardStatus
)
from app.schemas.schemas import (
    TrainingAssignmentRequest, SkillVerificationPayload,
    EmployeeSkillMatrixItem, EmployeeCompetencyOut, TrainingImpactResponse
)

def assign_training_for_anomaly(
    db: Session, request: TrainingAssignmentRequest
) -> TrainingAssignment:
    employee = db.query(Employee).filter(Employee.id == request.employee_id).first()
    store = db.query(Store).filter(Store.id == request.store_id).first()
    if not employee or not store:
        raise ValueError("Çalışan veya mağaza bulunamadı.")

    event_id = f"evt_trn_{uuid.uuid4().hex[:8]}"

    assignment = TrainingAssignment(
        event_id=event_id,
        employee_id=request.employee_id,
        store_id=request.store_id,
        trigger_reason=request.trigger_reason,
        course_code=request.course_code,
        course_name=request.course_name,
        deadline_days=request.deadline_days,
        is_mandatory=request.is_mandatory,
        status="ASSIGNED",
        baseline_kpi_value=request.baseline_kpi_value,
        target_kpi_value=request.target_kpi_value,
        financial_impact_try=request.financial_impact_try,
        assigned_at=datetime.utcnow()
    )
    db.add(assignment)

    # İlgili Aksiyon Kartı oluştur
    action_card = ActionCard(
        card_code=event_id,
        source_module="ACADEMY_TRAINING",
        title=f"Eğitim Ataması: {request.course_name} ({employee.full_name})",
        description=f"{store.name} mağazasında '{request.trigger_reason}' nedeniyle eğitim zorunlu kılındı.",
        root_cause=f"Operasyonel KPI sapması: Başlangıç {request.baseline_kpi_value} -> Hedef {request.target_kpi_value}",
        financial_impact_try=request.financial_impact_try,
        assigned_to=employee.full_name,
        approver="Mağaza Müdürü / Bölge Müdürü",
        priority="HIGH" if request.financial_impact_try > 20000 else "MEDIUM",
        status=ActionCardStatus.OPEN.value,
        deadline_date=date.today() + timedelta(days=request.deadline_days),
        created_at=datetime.utcnow()
    )
    db.add(action_card)

    db.commit()
    db.refresh(assignment)
    return assignment

def verify_and_record_certification(
    db: Session, payload: SkillVerificationPayload
) -> CertificationLog:
    employee = db.query(Employee).filter(Employee.employee_code == payload.employee_code).first()
    if not employee:
        raise ValueError(f"'{payload.employee_code}' kodlu çalışan bulunamadı.")

    cert_log = CertificationLog(
        certificate_event_id=payload.certification_event_id,
        employee_id=employee.id,
        course_code=payload.course_code,
        course_name=payload.course_name,
        exam_score=payload.exam_score,
        passed=payload.passed,
        certificate_qr_url=payload.certificate_qr_url,
        issued_at=payload.completion_date or datetime.utcnow()
    )
    db.add(cert_log)

    # Yetkinlik Skoru Güncelleme
    competency_code = payload.skill_delta.competency_area if payload.skill_delta else "GENERAL_COMPETENCY"
    comp = db.query(EmployeeCompetency).filter(
        EmployeeCompetency.employee_id == employee.id,
        EmployeeCompetency.competency_code == competency_code
    ).first()

    new_score = payload.skill_delta.new_score if payload.skill_delta else payload.exam_score
    operational_level = (payload.skill_delta.unlocked_operational_role 
                         if payload.skill_delta and payload.skill_delta.unlocked_operational_role 
                         else ("SENIOR" if new_score >= 85 else "INTERMEDIATE"))

    if comp:
        comp.score = new_score
        comp.operational_level = operational_level
        comp.last_evaluated_at = datetime.utcnow()
    else:
        comp = EmployeeCompetency(
            employee_id=employee.id,
            competency_code=competency_code,
            competency_name=payload.course_name,
            score=new_score,
            operational_level=operational_level,
            last_evaluated_at=datetime.utcnow()
        )
        db.add(comp)

    # Açık olan TrainingAssignment'ı tamamla
    active_assignment = db.query(TrainingAssignment).filter(
        TrainingAssignment.employee_id == employee.id,
        TrainingAssignment.course_code == payload.course_code,
        TrainingAssignment.status.in_(["ASSIGNED", "IN_PROGRESS"])
    ).first()

    if active_assignment:
        active_assignment.status = "COMPLETED"
        active_assignment.completed_at = datetime.utcnow()
        # KPI düzelme simülasyonu (hedefe ulaşma)
        active_assignment.post_training_kpi_value = active_assignment.target_kpi_value

        # Aksiyon Kartını Çözümlendi olarak güncelle
        action_card = db.query(ActionCard).filter(
            ActionCard.card_code == active_assignment.event_id
        ).first()
        if action_card:
            action_card.status = ActionCardStatus.RESOLVED.value
            action_card.resolved_at = datetime.utcnow()
            action_card.actual_recovered_try = active_assignment.financial_impact_try * 0.85
            action_card.resolution_evidence = f"Perakende Kariyer Akademisi Sertifikası #{payload.certification_event_id} (Sınav Puanı: {payload.exam_score})"

    db.commit()
    db.refresh(cert_log)
    return cert_log

def get_store_skill_matrix(db: Session, store_id: Optional[int] = None) -> List[EmployeeSkillMatrixItem]:
    query = db.query(Employee).filter(Employee.is_active == True)
    if store_id:
        query = query.filter(Employee.store_id == store_id)
    
    employees = query.all()
    matrix = []
    for emp in employees:
        comps = [
            EmployeeCompetencyOut(
                id=c.id,
                competency_code=c.competency_code,
                competency_name=c.competency_name,
                score=c.score,
                operational_level=c.operational_level,
                last_evaluated_at=c.last_evaluated_at
            ) for c in emp.competencies
        ]
        active_trainings = db.query(TrainingAssignment).filter(
            TrainingAssignment.employee_id == emp.id,
            TrainingAssignment.status.in_(["ASSIGNED", "IN_PROGRESS"])
        ).count()
        cert_count = len(emp.certifications)

        matrix.append(EmployeeSkillMatrixItem(
            employee_id=emp.id,
            employee_code=emp.employee_code,
            full_name=emp.full_name,
            store_id=emp.store_id,
            store_name=emp.store.name if emp.store else f"Mağaza #{emp.store_id}",
            department=emp.department,
            job_title=emp.job_title,
            is_active=emp.is_active,
            competencies=comps,
            active_training_count=active_trainings,
            certified_count=cert_count
        ))
    return matrix

def get_training_impact_report(db: Session, training_id: int) -> TrainingImpactResponse:
    training = db.query(TrainingAssignment).filter(TrainingAssignment.id == training_id).first()
    if not training:
        raise ValueError("Eğitim kaydı bulunamadı.")

    post_kpi = training.post_training_kpi_value if training.post_training_kpi_value is not None else training.baseline_kpi_value
    improvement_pct = 0.0
    if training.baseline_kpi_value > 0:
        improvement_pct = round(((post_kpi - training.baseline_kpi_value) / training.baseline_kpi_value) * 100.0, 2)

    saved_try = round(training.financial_impact_try * (min(100.0, max(0.0, abs(improvement_pct))) / 100.0), 2)
    is_goal = post_kpi >= training.target_kpi_value if training.target_kpi_value >= training.baseline_kpi_value else post_kpi <= training.target_kpi_value

    return TrainingImpactResponse(
        training_id=training.id,
        event_id=training.event_id,
        employee_name=training.employee.full_name if training.employee else "Bilinmeyen",
        job_title=training.employee.job_title if training.employee else "-",
        store_name=training.store.name if training.store else "-",
        course_name=training.course_name,
        status=training.status,
        trigger_reason=training.trigger_reason,
        baseline_kpi_value=training.baseline_kpi_value,
        target_kpi_value=training.target_kpi_value,
        post_training_kpi_value=training.post_training_kpi_value,
        kpi_improvement_pct=improvement_pct,
        financial_impact_try=training.financial_impact_try,
        financial_saved_try=saved_try,
        is_goal_achieved=is_goal
    )
