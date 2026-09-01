from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.entities import Store
from app.schemas.schemas import (
    StoreOut, StoreInventoryHealthSummary, StoreStockHealthExportFilterRequest
)
from app.services.store_service import StoreService

router = APIRouter(prefix="/stores", tags=["Mağaza & Stok Sağlığı Yönetimi"])

@router.get("", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    """Ana depo ve şubeleri listeler."""
    return db.query(Store).all()

@router.get("/inventory-health", response_model=StoreInventoryHealthSummary)
def get_store_inventory_health(
    store_id: Optional[int] = None,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    brand: Optional[str] = None,
    buyer_id: Optional[int] = None,
    health_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Mağaza Bazında Ürün Stok Sağlığı ve Sınıflandırması:
    - Yetersiz Stok (Kritik / Yok Satma Riski)
    - Atıl Stok (>45 Gün / Fazla Stok)
    - Ölü Stok (Son 90 Gün Hareketsiz)
    - Sağlıklı Stok
    - Kategori, Üretici, Marka ve Satın Almacı bazında detay döküm
    """
    return StoreService.get_inventory_health_report(
        db,
        store_id=store_id,
        category_id=category_id,
        supplier_id=supplier_id,
        brand=brand,
        buyer_id=buyer_id,
        health_status=health_status,
        search=search
    )

@router.get("/inventory-health/export")
def export_store_inventory_health(
    store_id: Optional[int] = None,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    brand: Optional[str] = None,
    buyer_id: Optional[int] = None,
    health_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Filtrelenen mağaza stok sağlığı listesini Excel (.xlsx) olarak indirir."""
    excel_stream = StoreService.export_inventory_health_to_excel(
        db,
        store_id=store_id,
        category_id=category_id,
        supplier_id=supplier_id,
        brand=brand,
        buyer_id=buyer_id,
        health_status=health_status,
        search=search
    )
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=SmartRetail_Magaza_Stok_Sagligi_Raporu.xlsx"
        }
    )

@router.post("/inventory-health/export-filtered")
def export_filtered_store_inventory_health(
    req: StoreStockHealthExportFilterRequest,
    db: Session = Depends(get_db)
):
    """UI'da filtrelenen kalemlere göre özel Excel (.xlsx) üretir ve indirir."""
    excel_stream = StoreService.export_inventory_health_to_excel(
        db,
        store_id=req.store_id,
        category_id=req.category_id,
        supplier_id=req.supplier_id,
        brand=req.brand,
        buyer_id=req.buyer_id,
        health_status=req.health_status,
        search=req.search,
        item_ids=req.item_ids
    )
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=SmartRetail_Magaza_Stok_Sagligi_Filtreli.xlsx"
        }
    )
