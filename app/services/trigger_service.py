import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import (
    ActionCard, ActionCardStatus, ActionCardPriority, TriggerEventLog,
    Inventory, Product, Store, Employee, TrainingAssignment, CRMEventLog
)
from app.schemas.schemas import (
    ActionCardCreate, ActionCardResolveRequest, ActionCardOut,
    TriggerAuditRunResponse
)
from app.services.crm_service import dispatch_overstock_to_crm
from app.services.academy_service import assign_training_for_anomaly
from app.schemas.schemas import TrainingAssignmentRequest

def create_action_card(db: Session, data: ActionCardCreate) -> ActionCard:
    card_code = f"ACT_{uuid.uuid4().hex[:8].upper()}"
    card = ActionCard(
        card_code=card_code,
        source_module=data.source_module,
        title=data.title,
        description=data.description,
        root_cause=data.root_cause,
        financial_impact_try=data.financial_impact_try,
        assigned_to=data.assigned_to,
        approver=data.approver,
        priority=data.priority,
        status=ActionCardStatus.OPEN.value,
        deadline_date=data.deadline_date or (date.today() + timedelta(days=7)),
        created_at=datetime.utcnow()
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

def list_action_cards(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source_module: Optional[str] = None,
    limit: int = 100
) -> List[ActionCardOut]:
    query = db.query(ActionCard)
    if status:
        query = query.filter(ActionCard.status == status)
    if priority:
        query = query.filter(ActionCard.priority == priority)
    if source_module:
        query = query.filter(ActionCard.source_module == source_module)
    
    cards = query.order_by(ActionCard.created_at.desc()).limit(limit).all()
    return [ActionCardOut.model_validate(c) for c in cards]

def resolve_action_card(
    db: Session, card_id: int, data: ActionCardResolveRequest
) -> ActionCardOut:
    card = db.query(ActionCard).filter(ActionCard.id == card_id).first()
    if not card:
        raise ValueError("Aksiyon kartı bulunamadı.")

    card.status = ActionCardStatus.RESOLVED.value
    card.resolution_evidence = data.resolution_evidence
    card.actual_recovered_try = data.actual_recovered_try
    card.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(card)
    return ActionCardOut.model_validate(card)

def run_comprehensive_audit(db: Session) -> TriggerAuditRunResponse:
    anomalies_count = 0
    action_cards_created = 0
    crm_events_dispatched = 0
    training_assignments_created = 0
    summary_messages = []

    # 1. Fazla Stok Taraması & XPlusCRM Tetikleyicisi
    overstocked_inventories = db.query(Inventory).join(Product).join(Store).filter(
        Store.type == "STORE",
        Inventory.quantity_on_hand > 50.0
    ).limit(3).all()

    for inv in overstocked_inventories:
        excess_qty = round(inv.quantity_on_hand * 0.6, 1)
        if excess_qty > 10:
            crm_log = dispatch_overstock_to_crm(db, inv.store_id, inv.product_id, excess_qty)
            crm_events_dispatched += 1
            anomalies_count += 1
            
            # Aksiyon Kartı Aç
            card = ActionCard(
                card_code=crm_log.event_id,
                source_module="EXCESS_STOCK",
                title=f"Fazla Stok Tasfiye: {inv.product.name} ({inv.store.name})",
                description=f"{inv.store.name} mağazasında {excess_qty} adet fazla stok tespit edildi. XPlusCRM hedeflenmiş kampanya tetiklendi.",
                root_cause="Düşük satış hızı ve yüksek emniyet stoğu",
                financial_impact_try=round(excess_qty * inv.product.sale_price, 2),
                assigned_to="Kategori Yöneticisi / CRM Ekibi",
                approver="Ticari Direktör",
                priority=ActionCardPriority.HIGH.value,
                status=ActionCardStatus.IN_PROGRESS.value,
                deadline_date=date.today() + timedelta(days=5),
                created_at=datetime.utcnow()
            )
            db.add(card)
            action_cards_created += 1
            summary_messages.append(f"XPlusCRM: {inv.store.name} - {inv.product.name} için {excess_qty} adet kampanya tetiklendi.")

    # 2. Taze Reyon / Operasyonel Hata & Akademi Eğitim Tetikleyicisi
    meat_employees = db.query(Employee).filter(
        Employee.department == "MEAT_AND_BUTCHERY",
        Employee.is_active == True
    ).limit(2).all()

    for emp in meat_employees:
        # Randıman sapması simülasyonu
        req = TrainingAssignmentRequest(
            employee_id=emp.id,
            store_id=emp.store_id,
            trigger_reason="CARCASS_YIELD_DEFICIT",
            course_code="CRS_MEAT_YIELD_OPT_101",
            course_name="Karkas Et Randımanı ve Fire Azaltma Uzmanlığı",
            deadline_days=5,
            is_mandatory=True,
            baseline_kpi_value=71.2,
            target_kpi_value=78.5,
            financial_impact_try=32500.0
        )
        assignment = assign_training_for_anomaly(db, req)
        training_assignments_created += 1
        anomalies_count += 1
        action_cards_created += 1
        summary_messages.append(f"Akademi: {emp.full_name} ({emp.store.name}) için '{req.course_name}' eğitimi atandı.")

    # Tetikleyici Logu Kaydet
    trigger_log = TriggerEventLog(
        trigger_type="COMPREHENSIVE_SYSTEM_AUDIT",
        source_module="TRIGGER_ENGINE",
        details=f"Anomaliler: {anomalies_count}, Aksiyonlar: {action_cards_created}, CRM: {crm_events_dispatched}, Akademi: {training_assignments_created}",
        target_system="SMART_RETAIL_ECOSYSTEM",
        status="SUCCESS",
        created_at=datetime.utcnow()
    )
    db.add(trigger_log)
    db.commit()

    return TriggerAuditRunResponse(
        audit_timestamp=datetime.utcnow(),
        anomalies_detected_count=anomalies_count,
        action_cards_created_count=action_cards_created,
        crm_events_dispatched_count=crm_events_dispatched,
        training_assignments_created_count=training_assignments_created,
        summary_messages=summary_messages
    )
