import json
import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import (
    Product, Inventory, Store, CRMEventLog, CRMCampaignFeedback,
    ActionCard, ActionCardStatus
)
from app.schemas.schemas import (
    CRMSimulationRequest, CRMSimulationResponse,
    CRMCampaignFeedbackPayload, CRMCampaignInsightItem
)

def simulate_overstock_liquidation(
    db: Session, store_id: int, product_id: int, max_discount_pct: float = 20.0
) -> CRMSimulationResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    store = db.query(Store).filter(Store.id == store_id).first()
    if not product or not store:
        raise ValueError("Ürün veya mağaza bulunamadı.")

    inventory = db.query(Inventory).filter(
        Inventory.store_id == store_id,
        Inventory.product_id == product_id
    ).first()

    current_stock = inventory.quantity_on_hand if inventory else 0.0
    target_stock = product.safety_stock_days * 2.0  # 14-21 gün
    excess_stock = max(0.0, current_stock - target_stock)
    if excess_stock == 0.0:
        excess_stock = current_stock * 0.5

    discount_rate = min(max_discount_pct / 100.0, 0.35)
    promo_price = round(product.sale_price * (1.0 - discount_rate), 2)

    target_customers = int(max(50, excess_stock * 3.5))
    conversion_rate = 32.5  # %32.5 dönüşüm
    expected_units_sold = min(excess_stock, round(target_customers * (conversion_rate / 100.0)))
    estimated_revenue = round(expected_units_sold * promo_price, 2)
    estimated_basket_lift = round(expected_units_sold * 180.0, 2)
    estimated_liquidation_days = max(3, int(excess_stock / max(1.0, expected_units_sold / 5.0)))

    return CRMSimulationResponse(
        product_id=product.id,
        product_name=product.name,
        store_id=store.id,
        store_name=store.name,
        excess_stock_qty=excess_stock,
        current_sale_price=product.sale_price,
        suggested_promo_price=promo_price,
        discount_pct=round(discount_rate * 100.0, 1),
        estimated_target_customers=target_customers,
        estimated_conversion_rate_pct=conversion_rate,
        estimated_revenue_try=estimated_revenue,
        estimated_basket_lift_try=estimated_basket_lift,
        estimated_liquidation_days=estimated_liquidation_days
    )

def dispatch_overstock_to_crm(
    db: Session, store_id: int, product_id: int, excess_units: float
) -> CRMEventLog:
    product = db.query(Product).filter(Product.id == product_id).first()
    store = db.query(Store).filter(Store.id == store_id).first()
    if not product or not store:
        raise ValueError("Ürün veya mağaza bulunamadı.")

    event_id = f"evt_stk_{uuid.uuid4().hex[:8]}"
    suggested_price = round(product.sale_price * 0.82, 2)

    payload = {
        "event_id": event_id,
        "event_type": "INVENTORY_OVERSTOCK_ALERT",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "store_id": f"str_{store.id}",
            "store_name": store.name,
            "sku": product.barcode,
            "product_name": product.name,
            "excess_stock_units": excess_units,
            "current_shelf_price": product.sale_price,
            "suggested_promo_price": suggested_price,
            "target_customer_count": int(excess_units * 3.5)
        }
    }

    crm_log = CRMEventLog(
        event_id=event_id,
        event_type="INVENTORY_OVERSTOCK_ALERT",
        store_id=store_id,
        product_id=product_id,
        payload_json=json.dumps(payload, ensure_ascii=False),
        status="DISPATCHED",
        created_at=datetime.utcnow()
    )
    db.add(crm_log)
    db.commit()
    db.refresh(crm_log)
    return crm_log

def record_crm_campaign_feedback(
    db: Session, payload: CRMCampaignFeedbackPayload
) -> CRMCampaignFeedback:
    feedback = CRMCampaignFeedback(
        campaign_id=payload.campaign_id,
        origin_event_id=payload.origin_event_id,
        targeted_customers=payload.targeted_customers,
        messages_delivered=payload.messages_delivered,
        coupons_redeemed=payload.coupons_redeemed_in_store,
        conversion_rate_pct=payload.conversion_rate_pct,
        total_revenue_generated_try=payload.total_revenue_generated_try,
        units_sold=payload.units_sold,
        remaining_excess_units=payload.remaining_excess_units,
        incremental_basket_revenue_try=payload.incremental_basket_revenue_try,
        dominant_segment=payload.dominant_segment or "ACTIVE_LOYALTY_SHOPPERS",
        avg_total_basket_value_try=payload.avg_total_basket_value_try,
        churn_prevented_customer_count=payload.churn_prevented_customer_count,
        received_at=datetime.utcnow()
    )
    db.add(feedback)

    if payload.origin_event_id:
        action_card = db.query(ActionCard).filter(
            ActionCard.card_code == payload.origin_event_id
        ).first()
        if action_card:
            action_card.actual_recovered_try = payload.total_revenue_generated_try + payload.incremental_basket_revenue_try
            action_card.resolution_evidence = f"XPlusCRM Kampanyası #{payload.campaign_id} ile {payload.units_sold} adet satıldı. Dönüşüm: %{payload.conversion_rate_pct}"
            action_card.status = ActionCardStatus.RESOLVED.value
            action_card.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(feedback)
    return feedback

def get_crm_campaign_insights(db: Session, limit: int = 50) -> List[CRMCampaignInsightItem]:
    feedbacks = db.query(CRMCampaignFeedback).order_by(CRMCampaignFeedback.received_at.desc()).limit(limit).all()
    results = []
    for f in feedbacks:
        results.append(CRMCampaignInsightItem(
            id=f.id,
            campaign_id=f.campaign_id,
            origin_event_id=f.origin_event_id,
            targeted_customers=f.targeted_customers,
            coupons_redeemed=f.coupons_redeemed,
            conversion_rate_pct=f.conversion_rate_pct,
            total_revenue_try=f.total_revenue_generated_try,
            units_sold=f.units_sold,
            incremental_basket_revenue_try=f.incremental_basket_revenue_try,
            dominant_segment=f.dominant_segment,
            avg_total_basket_value_try=f.avg_total_basket_value_try,
            churn_prevented_customer_count=f.churn_prevented_customer_count,
            received_at=f.received_at
        ))
    return results
