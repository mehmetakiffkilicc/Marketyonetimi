from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.schemas import (
    PurchasingWorkbenchResponse, CreatePurchaseOrderRequest, PurchaseOrderOut
)
from app.services.purchasing_service import PurchasingService
from app.models.entities import Supplier, Category, PurchaseOrder

router = APIRouter(prefix="/purchasing", tags=["Satın Alma & Sipariş"])

@router.get("/workbench", response_model=PurchasingWorkbenchResponse)
def get_purchasing_workbench_filtered(
    supplier_id: Optional[int] = None,
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Satın alma uzmanı sipariş ekranı (Üretici, Marka ve/veya Kategori bazlı filtreleme):
    - Üretici Firma, Marka ve Kategori seçimi
    - Seçim bazında aktif hedef yeter gün ve fiili ortalama yeter gün
    - Son 3 aylık fiili satışlar & kampanyalar
    - 3 aylık AI talep tahmini ve önerilen sipariş miktarları
    """
    try:
        return PurchasingService.get_workbench(db, supplier_id=supplier_id, category_id=category_id, brand=brand)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/brands", response_model=List[str])
def list_brands(
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Üreticiye bağlı veya tüm sistemdeki markaları listeler."""
    return PurchasingService.get_brands(db, supplier_id=supplier_id)

@router.get("/workbench/{supplier_id}", response_model=PurchasingWorkbenchResponse)
def get_purchasing_workbench(supplier_id: int, db: Session = Depends(get_db)):
    """Tedarikçi bazlı sipariş ekranı."""
    try:
        return PurchasingService.get_supplier_workbench(db, supplier_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/target-days")
def set_target_days(
    target_days: int,
    supplier_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Seçili Marka veya Kategori için hedef yeter gün sayısını günceller."""
    if supplier_id:
        sup = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if sup:
            sup.target_days_of_inventory = target_days
    if category_id:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if cat:
            cat.target_turnover_days = target_days
    db.commit()
    return {"status": "ok", "target_days": target_days}

@router.post("/orders", response_model=PurchaseOrderOut)
def create_purchase_order(req: CreatePurchaseOrderRequest, db: Session = Depends(get_db)):
    """
    Satın alma siparişi oluşturur.
    Sipariş anında tanımlanan geleceğe dönük kampanyaları otomatik olarak sisteme bağlar ve takvime işler.
    """
    try:
        return PurchasingService.create_purchase_order(db, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi.responses import StreamingResponse
from datetime import date
from app.schemas.schemas import (
    PurchasingWorkbenchResponse, CreatePurchaseOrderRequest, PurchaseOrderOut,
    PurchaseOrdersReportResponse, PurchaseOrdersExportFilterRequest
)

@router.get("/orders/report", response_model=PurchaseOrdersReportResponse)
def get_purchase_orders_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Satın Alma Direktörü, Genel Müdür ve CFO için Tarih Seçimli Verilen Siparişler & Finansal Vade Raporu:
    - Teslimden itibaren yaklaşık ödeme tarihleri (Vade Takibi)
    - KDV Dahil toplam sipariş tutarları
    - Vadesi yaklaşan ödeme nakit projeksiyonu
    """
    return PurchasingService.get_purchase_orders_report(
        db, start_date=start_date, end_date=end_date, supplier_id=supplier_id, status=status
    )

@router.get("/orders/export")
def export_purchase_orders(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    buyer_name: Optional[str] = None,
    due_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Filtrelenen siparişleri, ürün kalemlerini ve vade günlerini doğrudan Excel (.xlsx) olarak indirir."""
    excel_stream = PurchasingService.export_purchase_orders_to_excel(
        db,
        start_date=start_date,
        end_date=end_date,
        supplier_id=supplier_id,
        status=status,
        buyer_name=buyer_name,
        due_status=due_status,
        search=search
    )
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=SmartRetail_Verilen_Siparisler_Vade_Raporu.xlsx"
        }
    )

@router.post("/orders/export-filtered")
def export_filtered_purchase_orders(
    req: PurchaseOrdersExportFilterRequest,
    db: Session = Depends(get_db)
):
    """UI'da filtrelenen sipariş kimliklerine (po_ids) göre özel Excel (.xlsx) üretir ve indirir."""
    excel_stream = PurchasingService.export_purchase_orders_to_excel(
        db,
        start_date=req.start_date,
        end_date=req.end_date,
        supplier_id=req.supplier_id,
        status=req.status,
        buyer_name=req.buyer_name,
        due_status=req.due_status,
        search=req.search,
        po_ids=req.po_ids
    )
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=SmartRetail_Filtrelenen_Siparisler_Vade_Raporu.xlsx"
        }
    )

@router.get("/orders", response_model=List[PurchaseOrderOut])
def list_purchase_orders(db: Session = Depends(get_db)):
    """Tüm satın alma siparişlerini listeler."""
    orders = db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).all()
    result = []
    for po in orders:
        result.append(PurchaseOrderOut(
            id=po.id,
            po_number=po.po_number,
            supplier_name=po.supplier.name if po.supplier else "-",
            buyer_name=po.buyer.name if po.buyer else "-",
            order_date=po.order_date,
            expected_delivery_date=po.expected_delivery_date,
            status=po.status,
            total_cost=po.total_cost,
            item_count=len(po.items),
            linked_campaign_count=len(po.linked_campaigns)
        ))
    return result
