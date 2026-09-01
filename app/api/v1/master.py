from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.entities import Product, Category, Store, User
from app.schemas.schemas import ProductOut, CategoryOut, StoreOut, UserOut

router = APIRouter(prefix="/master", tags=["Tanımlar & Ana Veriler"])

@router.get("/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    """Sistemdeki tüm ürün ve barkod tanımlarını listeler."""
    prods = db.query(Product).all()
    result = []
    for p in prods:
        result.append(ProductOut(
            id=p.id,
            barcode=p.barcode,
            name=p.name,
            category_id=p.category_id,
            category_name=p.category.name if p.category else None,
            supplier_id=p.supplier_id,
            supplier_name=p.supplier.name if p.supplier else None,
            unit=p.unit,
            purchase_price=p.purchase_price,
            sale_price=p.sale_price,
            vat_rate=p.vat_rate,
            shelf_life_days=p.shelf_life_days,
            safety_stock_days=p.safety_stock_days
        ))
    return result

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Kategori ağacını listeler."""
    return db.query(Category).all()

@router.get("/stores", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    """Ana depo ve şubeleri listeler."""
    return db.query(Store).all()

@router.get("/buyers", response_model=List[UserOut])
def list_buyers(db: Session = Depends(get_db)):
    """Satın almacıları ve yöneticileri listeler."""
    return db.query(User).all()

@router.patch("/categories/{category_id}/target-days", response_model=CategoryOut)
def update_category_target_days(category_id: int, target_days: int, db: Session = Depends(get_db)):
    """Kategori bazında hedef yeter gün / devir süresini günceller."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Kategori bulunamadı.")
    category.target_turnover_days = target_days
    db.commit()
    db.refresh(category)
    return category
