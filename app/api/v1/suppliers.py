from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.entities import Supplier, Product, Inventory, SalesHistory
from app.schemas.schemas import (
    SupplierOut, 
    SupplierScorecardItem, 
    UpdateSupplierTargetDaysRequest,
    UpdateSupplierParametersRequest,
    SupplierDetailResponse,
    SupplierProductDetailItem,
    UpdateProductParametersRequest,
    ProductOut
)
from app.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["Üretici / Tedarikçi Yönetimi"])

@router.get("", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    """Tüm üretici ve tedarikçi firmaları listeler."""
    return db.query(Supplier).all()

@router.get("/scorecards", response_model=List[SupplierScorecardItem])
def get_supplier_scorecards(
    supplier_id: Optional[int] = None,
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    buyer_id: Optional[int] = None,
    store_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Üretici Performans & Karne Analitiği (Kategori, Üretici, Marka, Satın Almacı ve Mağaza filtreleme destekli):
    - Üreticinin toplam fiziki stoğu, Dönem Başı / Dönem Sonu ve Ortalama Stok Maliyeti (TL)
    - Dönem Toplam Kârlılığı ve GMROI (Gross Margin Return on Inventory Investment) kârlılık oranı
    - Hedef ve fiili yeter gün sayıları (Days of Inventory) & Stok sağlık durumu
    - Son 3 aylık satış adedi, ciro ve kâr tutarı
    - Market toplam cirosu ve kârındaki % payı
    - BCG Matris segmentasyonu (Yıldız, Nakit İneği, Soru İşareti, Düşük Performans)
    """
    return SupplierService.get_all_scorecards(
        db,
        supplier_id=supplier_id,
        category_id=category_id,
        brand=brand,
        buyer_id=buyer_id,
        store_id=store_id
    )

@router.get("/{supplier_id}/detail", response_model=SupplierDetailResponse)
def get_supplier_detail(supplier_id: int, db: Session = Depends(get_db)):
    """Tedarikçinin tüm ürünlerini, stok, hız ve hedef parametreleriyle birlikte döner."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı.")
    
    products = db.query(Product).filter(Product.supplier_id == supplier_id).all()
    prod_ids = [p.id for p in products]

    inventories = db.query(Inventory).filter(Inventory.product_id.in_(prod_ids)).all() if prod_ids else []
    sales = db.query(SalesHistory).filter(SalesHistory.product_id.in_(prod_ids)).all() if prod_ids else []

    total_revenue = sum(s.gross_revenue for s in sales)
    total_cogs = sum(s.cogs for s in sales)
    total_profit = total_revenue - total_cogs
    total_stock_cost = sum(inv.quantity_on_hand * next((p.purchase_price for p in products if p.id == inv.product_id), 0.0) for inv in inventories)
    gmroi = round(total_profit / total_stock_cost, 2) if total_stock_cost > 0 else 0.0

    prod_items = []
    for p in products:
        p_inv = [i for i in inventories if i.product_id == p.id]
        p_stock_qty = sum(i.quantity_on_hand for i in p_inv)
        p_stock_cost = p_stock_qty * p.purchase_price

        p_sales = [s for s in sales if s.product_id == p.id]
        p_sold_qty = sum(s.quantity_sold for s in p_sales)
        p_daily_rate = (p_sold_qty / 90.0) if p_sold_qty > 0 else 0.1
        p_days_inv = round(p_stock_qty / p_daily_rate, 1)

        prod_items.append(SupplierProductDetailItem(
            id=p.id,
            barcode=p.barcode,
            name=p.name,
            brand=p.brand,
            category_id=p.category_id,
            category_name=p.category.name if p.category else "-",
            unit=p.unit,
            purchase_price=p.purchase_price,
            sale_price=p.sale_price,
            safety_stock_days=p.safety_stock_days,
            total_stock_qty=round(p_stock_qty, 1),
            total_stock_cost=round(p_stock_cost, 2),
            daily_sales_rate=round(p_daily_rate, 2),
            days_of_inventory=p_days_inv
        ))

    return SupplierDetailResponse(
        id=supplier.id,
        name=supplier.name,
        code=supplier.code,
        payment_term_days=supplier.payment_term_days,
        lead_time_days=supplier.lead_time_days,
        target_days_of_inventory=float(supplier.target_days_of_inventory or 21),
        min_order_amount=float(supplier.min_order_amount or 5000.0),
        contact_name=supplier.contact_name,
        phone=supplier.phone,
        total_stock_cost=round(total_stock_cost, 2),
        total_revenue_3m=round(total_revenue, 2),
        total_profit_3m=round(total_profit, 2),
        gmroi_ratio=gmroi,
        products=prod_items
    )

@router.patch("/{supplier_id}/parameters", response_model=SupplierOut)
def update_supplier_parameters(supplier_id: int, req: UpdateSupplierParametersRequest, db: Session = Depends(get_db)):
    """Üretici / Tedarikçi hedef yeter gün, teslim süresi, vade ve min sipariş parametrelerini günceller."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı.")
    
    if req.target_days_of_inventory is not None:
        supplier.target_days_of_inventory = int(req.target_days_of_inventory)
    if req.lead_time_days is not None:
        supplier.lead_time_days = req.lead_time_days
    if req.payment_term_days is not None:
        supplier.payment_term_days = req.payment_term_days
    if req.min_order_amount is not None:
        supplier.min_order_amount = req.min_order_amount
    
    db.commit()
    db.refresh(supplier)
    return supplier

@router.patch("/products/{product_id}/parameters", response_model=ProductOut)
def update_product_parameters(product_id: int, req: UpdateProductParametersRequest, db: Session = Depends(get_db)):
    """Ürün emniyet stoğu ve fiyat parametrelerini günceller."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    
    if req.safety_stock_days is not None:
        product.safety_stock_days = req.safety_stock_days
    if req.purchase_price is not None:
        product.purchase_price = req.purchase_price
    if req.sale_price is not None:
        product.sale_price = req.sale_price
    
    db.commit()
    db.refresh(product)
    return product

@router.patch("/{supplier_id}/target-days", response_model=SupplierOut)
def update_supplier_target_days(supplier_id: int, req: UpdateSupplierTargetDaysRequest, db: Session = Depends(get_db)):
    """Üretici / Tedarikçi için hedef yeter gün sayısını günceller."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı.")
    supplier.target_days_of_inventory = req.target_days_of_inventory
    db.commit()
    db.refresh(supplier)
    return supplier
