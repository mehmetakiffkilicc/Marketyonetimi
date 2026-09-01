import io
import pandas as pd
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import Campaign, CampaignProduct, Product, Inventory, PurchaseOrder
from app.schemas.schemas import CampaignReportItem, CampaignProductItemOut

class CampaignService:
    @staticmethod
    def get_campaign_reports(db: Session, category_id: Optional[int] = None, supplier_id: Optional[int] = None) -> List[CampaignReportItem]:
        campaigns = db.query(Campaign).order_by(Campaign.start_date.desc()).all()
        reports = []

        for c in campaigns:
            # Kampanya ürünleri
            camp_prods = db.query(CampaignProduct).filter(CampaignProduct.campaign_id == c.id).all()
            prod_items = []
            
            for cp in camp_prods:
                p = cp.product
                if not p:
                    continue
                if category_id and p.category_id != category_id:
                    continue
                if supplier_id and p.supplier_id != supplier_id:
                    continue

                shelf_price = cp.regular_shelf_price or p.sale_price
                disc_rate = cp.discount_rate or c.discount_rate or 0.15
                promo_price = cp.promotional_price or (shelf_price * (1.0 - disc_rate))
                
                prod_items.append(CampaignProductItemOut(
                    product_id=p.id,
                    barcode=p.barcode,
                    product_name=p.name,
                    category_name=p.category.name if p.category else "Genel",
                    supplier_name=p.supplier.name if p.supplier else "Genel",
                    regular_shelf_price=round(shelf_price, 2),
                    promotional_price=round(promo_price, 2),
                    discount_rate_pct=round(disc_rate * 100.0, 1),
                    target_sales_qty=round(cp.target_sales_qty or 0.0, 1),
                    application_channel=cp.application_channel or c.application_channel or "DİREKT_RAF"
                ))

            if (category_id or supplier_id) and not prod_items:
                continue

            # Hedef vs Gerçekleşen Başarı Oranı
            achievement_rate = (c.actual_sales_qty / c.target_sales_qty * 100.0) if c.target_sales_qty > 0 else 0.0

            # Kalan stok hesabı
            prod_ids = [cp.product_id for cp in camp_prods]
            inventories = db.query(Inventory).filter(Inventory.product_id.in_(prod_ids)).all() if prod_ids else []
            leftover_stock = sum(inv.quantity_on_hand for inv in inventories)

            po_number = c.created_from_po.po_number if c.created_from_po else None

            reports.append(CampaignReportItem(
                id=c.id,
                title=c.title,
                start_date=c.start_date,
                end_date=c.end_date,
                campaign_type=c.campaign_type,
                discount_rate=c.discount_rate,
                application_channel=c.application_channel or "DİREKT_RAF",
                status=c.status,
                target_sales_qty=round(c.target_sales_qty, 1),
                target_revenue=round(c.target_revenue, 2),
                actual_sales_qty=round(c.actual_sales_qty, 1),
                actual_revenue=round(c.actual_revenue, 2),
                achievement_rate_pct=round(achievement_rate, 1),
                leftover_stock_qty=round(leftover_stock, 1),
                created_from_po_number=po_number,
                products=prod_items
            ))

        return reports

    @staticmethod
    def export_campaigns_to_excel(db: Session, campaign_id: Optional[int] = None) -> io.BytesIO:
        """Kampanya planını ve ürünlerini biçimlendirilmiş Excel (xlsx) dosyasına aktarır."""
        query = db.query(Campaign)
        if campaign_id:
            query = query.filter(Campaign.id == campaign_id)
        campaigns = query.order_by(Campaign.start_date.asc()).all()

        rows = []
        for c in campaigns:
            camp_prods = db.query(CampaignProduct).filter(CampaignProduct.campaign_id == c.id).all()
            for cp in camp_prods:
                p = cp.product
                if not p:
                    continue
                shelf_price = cp.regular_shelf_price or p.sale_price
                disc_rate = cp.discount_rate or c.discount_rate or 0.15
                promo_price = cp.promotional_price or (shelf_price * (1.0 - disc_rate))
                target_qty = cp.target_sales_qty if cp.target_sales_qty > 0 else c.target_sales_qty
                target_rev = target_qty * promo_price
                app_chan = cp.application_channel or c.application_channel or "DİREKT_RAF"
                chan_label = "Direkt Raf İndirimi" if app_chan == "DİREKT_RAF" else ("Dijital Sadakat Kartı" if app_chan == "DİJİTAL_KART" else "Tüm Müşteriler & Dijital Kart")

                rows.append({
                    "Kampanya ID": c.id,
                    "Kampanya Başlığı": c.title,
                    "Başlangıç Tarihi": c.start_date.strftime("%d.%m.%Y"),
                    "Bitiş Tarihi": c.end_date.strftime("%d.%m.%Y"),
                    "Aktivite Süresi (Gün)": (c.end_date - c.start_date).days + 1,
                    "Kategori": p.category.name if p.category else "Genel",
                    "Üretici / Marka": p.supplier.name if p.supplier else "Genel",
                    "Barkod": p.barcode,
                    "Ürün Adı": p.name,
                    "Birim": p.unit,
                    "Normal Raf Satış Fiyatı (TL)": round(shelf_price, 2),
                    "Aktivite Satış Fiyatı (TL)": round(promo_price, 2),
                    "İndirim Oranı (%)": round(disc_rate * 100.0, 1),
                    "Uygulama Kanalı": chan_label,
                    "Hedef Satış Adedi": round(target_qty, 1),
                    "Hedeflenen Ciro (TL)": round(target_rev, 2),
                    "Gerçekleşen Satış Adedi": round(c.actual_sales_qty, 1) if c.actual_sales_qty > 0 else "-",
                    "Gerçekleşen Ciro (TL)": round(c.actual_revenue, 2) if c.actual_revenue > 0 else "-",
                    "Durum": "Planlandı" if c.status == "PLANNED" else ("Aktif" if c.status == "ACTIVE" else "Tamamlandı"),
                    "Bağlı Sipariş No": c.created_from_po.po_number if c.created_from_po else "Manuel"
                })

        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Kampanya_Plani', index=False)
        output.seek(0)
        return output

    @staticmethod
    def create_single_product_campaign(db: Session, req) -> dict:
        product = db.query(Product).filter(Product.id == req.product_id).first()
        if not product:
            raise ValueError("Ürün bulunamadı")

        shelf_price = req.shelf_price or product.sale_price
        disc_rate = req.discount_rate or 0.15
        promo_price = req.promotional_price or (shelf_price * (1.0 - disc_rate))
        target_qty = req.target_sales_qty or 0.0
        target_rev = target_qty * promo_price

        campaign = Campaign(
            title=req.title or f"{product.name} Kampanyası",
            start_date=req.start_date,
            end_date=req.end_date,
            campaign_type=req.campaign_type or "PERCENT_DISCOUNT",
            discount_rate=disc_rate,
            application_channel=req.application_channel or "DİREKT_RAF",
            status="PLANNED",
            target_sales_qty=round(target_qty, 1),
            target_revenue=round(target_rev, 2),
            actual_sales_qty=0.0,
            actual_revenue=0.0,
            notes=req.notes
        )
        db.add(campaign)
        db.flush()

        camp_prod = CampaignProduct(
            campaign_id=campaign.id,
            product_id=product.id,
            regular_shelf_price=round(shelf_price, 2),
            promotional_price=round(promo_price, 2),
            discount_rate=disc_rate,
            target_sales_qty=round(target_qty, 1),
            application_channel=req.application_channel or "DİREKT_RAF"
        )
        db.add(camp_prod)
        db.commit()
        db.refresh(campaign)

        return {
            "status": "success",
            "campaign_id": campaign.id,
            "title": campaign.title,
            "product_name": product.name,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "discount_rate": campaign.discount_rate,
            "promotional_price": promo_price,
            "application_channel": campaign.application_channel
        }
