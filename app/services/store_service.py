from typing import List, Optional
from datetime import date, timedelta
import io
import pandas as pd
from sqlalchemy.orm import Session
from app.models.entities import Store, Inventory, Product, Category, Supplier, User, SalesHistory
from app.schemas.schemas import StoreProductStockHealthItem, StoreInventoryHealthSummary

class StoreService:
    @staticmethod
    def get_inventory_health_report(
        db: Session,
        store_id: Optional[int] = None,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        brand: Optional[str] = None,
        buyer_id: Optional[int] = None,
        health_status: Optional[str] = None,
        search: Optional[str] = None
    ) -> StoreInventoryHealthSummary:
        
        inv_query = db.query(Inventory).join(Product, Inventory.product_id == Product.id).join(Store, Inventory.store_id == Store.id)

        if store_id:
            inv_query = inv_query.filter(Inventory.store_id == store_id)
        if category_id:
            inv_query = inv_query.filter(Product.category_id == category_id)
        if supplier_id:
            inv_query = inv_query.filter(Product.supplier_id == supplier_id)
        if brand:
            inv_query = inv_query.filter(Product.brand == brand)
        if buyer_id:
            inv_query = inv_query.filter(Product.buyer_id == buyer_id)

        records = inv_query.all()

        cutoff_30d = date(2026, 8, 1)
        cutoff_90d = date(2026, 6, 1)

        items: List[StoreProductStockHealthItem] = []

        for inv in records:
            p = inv.product
            st = inv.store
            if not p or not st:
                continue

            # Store sales in 30d & 90d
            sales_recs = db.query(SalesHistory).filter(
                SalesHistory.product_id == p.id,
                SalesHistory.store_id == st.id,
                SalesHistory.sale_date >= cutoff_90d
            ).all()

            qty_90d = sum(s.quantity_sold for s in sales_recs) if sales_recs else 0.0
            qty_30d = sum(s.quantity_sold for s in sales_recs if s.sale_date >= cutoff_30d) if sales_recs else 0.0

            daily_rate = round(qty_90d / 90.0, 2) if qty_90d > 0 else (round(qty_30d / 30.0, 2) if qty_30d > 0 else 0.0)
            stock_qty = round(inv.quantity_on_hand, 1)
            stock_cost = round(stock_qty * p.purchase_price, 2)

            # Classify Stock Health
            # 1. Ölü Stok: Stok > 0 ama 90 günde neredeyse hiç satmıyor
            if stock_qty > 0 and qty_90d <= 2.0:
                h_status = "DEAD_STOCK"
                h_label = "Ölü Stok (Hareketsiz)"
                days_inv = 999.0
                action = "⚡ İndirimle Erit / Tedarikçiye İade"
            # 2. Satış hızı olan ürünler
            elif daily_rate > 0:
                days_inv = round(stock_qty / daily_rate, 1)
                if days_inv < 5.0 or stock_qty <= 0:
                    h_status = "CRITICAL_LOW"
                    h_label = "Yetersiz Stok"
                    action = "🚀 Acil Sipariş / Depodan Sevk"
                elif days_inv > 45.0:
                    h_status = "OVERSTOCK"
                    h_label = "Atıl Stok (>45g)"
                    action = "🎯 Kampanya Yap / Şubelere Dağıt"
                else:
                    h_status = "HEALTHY"
                    h_label = "Sağlıklı Stok"
                    action = "✅ Normal Devir"
            # 3. Satış hızı 0 olan
            else:
                if stock_qty > 0:
                    h_status = "DEAD_STOCK"
                    h_label = "Ölü Stok (Hareketsiz)"
                    days_inv = 999.0
                    action = "⚡ İndirimle Erit / İade"
                else:
                    h_status = "CRITICAL_LOW"
                    h_label = "Yetersiz Stok (0 Adet)"
                    days_inv = 0.0
                    action = "🚀 Acil Sipariş"

            # Filter by health_status
            if health_status and h_status != health_status:
                continue

            # Filter by search keyword
            if search:
                q = search.lower().strip()
                in_name = q in p.name.lower() or q in p.barcode.lower()
                in_brand = p.brand and q in p.brand.lower()
                in_store = q in st.name.lower()
                in_sup = p.supplier and q in p.supplier.name.lower()
                in_buyer = p.buyer and q in p.buyer.name.lower()
                if not (in_name or in_brand or in_store or in_sup or in_buyer):
                    continue

            buyer_obj = p.buyer
            buyer_title = buyer_obj.name if buyer_obj else "Satın Alma"

            items.append(StoreProductStockHealthItem(
                id=inv.id,
                store_id=st.id,
                store_name=st.name,
                store_type=st.type,
                product_id=p.id,
                barcode=p.barcode,
                product_name=p.name,
                brand=p.brand or "Genel",
                category_id=p.category_id,
                category_name=p.category.name if p.category else "Genel",
                supplier_id=p.supplier_id,
                supplier_name=p.supplier.name if p.supplier else "Genel",
                buyer_id=p.buyer_id,
                buyer_name=buyer_title,
                unit=p.unit,
                purchase_price=round(p.purchase_price, 2),
                sale_price=round(p.sale_price, 2),
                current_stock_qty=stock_qty,
                current_stock_cost=stock_cost,
                daily_sales_rate=daily_rate,
                days_of_inventory=days_inv if days_inv < 999 else 999.0,
                sales_30d_qty=round(qty_30d, 1),
                sales_90d_qty=round(qty_90d, 1),
                stock_health_status=h_status,
                health_status_label=h_label,
                action_recommendation=action
            ))

        # Calculate Group Summaries
        total_qty = sum(it.current_stock_qty for it in items)
        total_cost = sum(it.current_stock_cost for it in items)

        crit_items = [it for it in items if it.stock_health_status == "CRITICAL_LOW"]
        over_items = [it for it in items if it.stock_health_status == "OVERSTOCK"]
        dead_items = [it for it in items if it.stock_health_status == "DEAD_STOCK"]
        health_items = [it for it in items if it.stock_health_status == "HEALTHY"]

        valid_days = [it.days_of_inventory for it in items if it.days_of_inventory < 900 and it.days_of_inventory > 0]
        avg_days = round(sum(valid_days) / len(valid_days), 1) if valid_days else 21.0

        return StoreInventoryHealthSummary(
            total_products_count=len(items),
            total_stock_qty=round(total_qty, 1),
            total_stock_cost=round(total_cost, 2),
            critical_stock_count=len(crit_items),
            critical_stock_cost=round(sum(it.current_stock_cost for it in crit_items), 2),
            overstock_count=len(over_items),
            overstock_cost=round(sum(it.current_stock_cost for it in over_items), 2),
            dead_stock_count=len(dead_items),
            dead_stock_cost=round(sum(it.current_stock_cost for it in dead_items), 2),
            healthy_stock_count=len(health_items),
            healthy_stock_cost=round(sum(it.current_stock_cost for it in health_items), 2),
            avg_days_of_inventory=avg_days,
            items=items
        )

    @staticmethod
    def export_inventory_health_to_excel(
        db: Session,
        store_id: Optional[int] = None,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        brand: Optional[str] = None,
        buyer_id: Optional[int] = None,
        health_status: Optional[str] = None,
        search: Optional[str] = None,
        item_ids: Optional[List[int]] = None
    ) -> io.BytesIO:
        report = StoreService.get_inventory_health_report(
            db,
            store_id=store_id,
            category_id=category_id,
            supplier_id=supplier_id,
            brand=brand,
            buyer_id=buyer_id,
            health_status=health_status,
            search=search
        )

        filtered_items = report.items
        if item_ids and len(item_ids) > 0:
            filtered_items = [it for it in filtered_items if it.id in item_ids]

        rows = []
        for it in filtered_items:
            rows.append({
                "Mağaza": it.store_name,
                "Mağaza Tipi": "Ana Depo" if it.store_type == "CENTRAL_WAREHOUSE" else "Şube",
                "Barkod": it.barcode,
                "Ürün Adı": it.product_name,
                "Marka": it.brand,
                "Kategori": it.category_name,
                "Üretici Firma": it.supplier_name,
                "Satın Alma Sorumlusu": it.buyer_name,
                "Mevcut Stok Adedi": it.current_stock_qty,
                "Birim": it.unit,
                "Birim Alış (TL)": it.purchase_price,
                "Birim Satış (TL)": it.sale_price,
                "Toplam Stok Maliyeti (TL)": it.current_stock_cost,
                "Günlük Satış Hızı": it.daily_sales_rate,
                "30 Günlük Satış (Adet)": it.sales_30d_qty,
                "90 Günlük Satış (Adet)": it.sales_90d_qty,
                "Yeter Gün Sayısı": it.days_of_inventory if it.days_of_inventory < 900 else "Hareketsiz / 0 Satış",
                "Stok Sağlık Durumu": it.health_status_label,
                "Aksiyon / Öneri": it.action_recommendation
            })

        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Magaza_Stok_Sagligi', index=False)
        output.seek(0)
        return output
