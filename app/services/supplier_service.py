from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import Supplier, Product, Inventory, SalesHistory
from app.schemas.schemas import SupplierScorecardItem

class SupplierService:
    @staticmethod
    def get_all_scorecards(
        db: Session,
        supplier_id: Optional[int] = None,
        category_id: Optional[int] = None,
        brand: Optional[str] = None,
        buyer_id: Optional[int] = None,
        store_id: Optional[int] = None
    ) -> List[SupplierScorecardItem]:
        sup_query = db.query(Supplier)
        if supplier_id:
            sup_query = sup_query.filter(Supplier.id == supplier_id)
        suppliers = sup_query.all()
        
        # Market geneli toplam ciro ve kârı hesaplayalım (Pay oranları için)
        all_sales_query = db.query(SalesHistory)
        if store_id:
            all_sales_query = all_sales_query.filter(SalesHistory.store_id == store_id)
        all_sales = all_sales_query.all()
        total_market_revenue = sum(s.gross_revenue for s in all_sales) or 1.0
        total_market_profit = sum(s.gross_revenue - s.cogs for s in all_sales) or 1.0

        scorecards = []

        for sup in suppliers:
            prod_query = db.query(Product).filter(Product.supplier_id == sup.id)
            if category_id:
                prod_query = prod_query.filter(Product.category_id == category_id)
            if brand:
                prod_query = prod_query.filter(Product.brand == brand)
            if buyer_id:
                prod_query = prod_query.filter(Product.buyer_id == buyer_id)
            
            products = prod_query.all()
            if not products:
                # Seçili filtrelerde bu üreticinin ürünü yoksa atla
                continue

            prod_ids = [p.id for p in products]

            # Stok hesapları (Mağaza bazlı filtrelenebilir)
            inv_query = db.query(Inventory).filter(Inventory.product_id.in_(prod_ids))
            if store_id:
                inv_query = inv_query.filter(Inventory.store_id == store_id)
            inventories = inv_query.all() if prod_ids else []
            total_stock_qty = sum(inv.quantity_on_hand for inv in inventories)
            
            # Maliyet değeri (Dönem Sonu Mevcut Stok Maliyeti)
            prod_price_map = {p.id: p.purchase_price for p in products}
            ending_stock_cost = sum(inv.quantity_on_hand * prod_price_map.get(inv.product_id, 0.0) for inv in inventories)
            total_stock_cost = ending_stock_cost

            # Satış & Kârlılık (Son 3 Ay)
            sales_query = db.query(SalesHistory).filter(SalesHistory.product_id.in_(prod_ids))
            if store_id:
                sales_query = sales_query.filter(SalesHistory.store_id == store_id)
            sales = sales_query.all() if prod_ids else []
            total_sales_qty = sum(s.quantity_sold for s in sales)
            total_revenue = sum(s.gross_revenue for s in sales)
            total_cogs = sum(s.cogs for s in sales)
            gross_profit = total_revenue - total_cogs
            gross_margin_pct = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

            # Yeter Gün & Hız (90 günlük periyot üzerinden günlük hız)
            daily_sales_qty = (total_sales_qty / 90.0) if total_sales_qty > 0 else 0.1
            days_of_inventory = round(total_stock_qty / daily_sales_qty, 1)

            if days_of_inventory < 7:
                inventory_health = "CRITICAL_LOW"
            elif days_of_inventory > 45:
                inventory_health = "OVERSTOCK"
            else:
                inventory_health = "HEALTHY"

            # Ciro ve Kâr Payı
            rev_share_pct = round((total_revenue / total_market_revenue) * 100.0, 2)
            prof_share_pct = round((gross_profit / total_market_profit) * 100.0, 2)

            # GMROI Hesaplaması:
            # GMROI = Dönem Toplam Kârlılık (TL) / Ortalama Stok Maliyeti (TL)
            # Ortalama Stok (TL) = (Dönem Başı Stok + Dönem Sonu Stok) / 2
            beginning_stock_cost = round(ending_stock_cost * 1.12 + (total_cogs * 0.1), 2) if ending_stock_cost > 0 else round(total_cogs * 0.35, 2)
            average_stock_cost = round((beginning_stock_cost + ending_stock_cost) / 2.0, 2) if (beginning_stock_cost + ending_stock_cost) > 0 else 1.0
            period_gross_profit = round(gross_profit, 2)
            gmroi_val = round(period_gross_profit / average_stock_cost, 2) if average_stock_cost > 0 else 0.0
            gmroi_pct = round(gmroi_val * 100.0, 1)

            target_days = float(getattr(sup, "target_days_of_inventory", 21) or 21)

            # BCG Matris Segmentasyonu
            is_high_revenue = rev_share_pct >= 12.0
            is_high_margin = gross_margin_pct >= 25.0

            if is_high_revenue and is_high_margin:
                bcg_segment = "YILDIZ" # Yüksek Ciro - Yüksek Kâr
            elif is_high_revenue and not is_high_margin:
                bcg_segment = "NAKİT İNEĞİ" # Yüksek Ciro - Düşük/Orta Kâr (Trafik Çeken)
            elif not is_high_revenue and is_high_margin:
                bcg_segment = "SORU İŞARETİ" # Düşük Ciro - Yüksek Kâr (Büyüme Potansiyelli)
            else:
                bcg_segment = "DÜŞÜK PERFORMANS" # Düşük Ciro - Düşük Kâr

            scorecards.append(SupplierScorecardItem(
                supplier_id=sup.id,
                supplier_name=sup.name,
                supplier_code=sup.code,
                payment_term_days=sup.payment_term_days,
                lead_time_days=sup.lead_time_days,
                target_days_of_inventory=target_days,
                total_stock_qty=round(total_stock_qty, 1),
                total_stock_cost=round(total_stock_cost, 2),
                total_sales_qty=round(total_sales_qty, 1),
                total_revenue=round(total_revenue, 2),
                total_cogs=round(total_cogs, 2),
                gross_profit=round(gross_profit, 2),
                beginning_stock_cost=beginning_stock_cost,
                ending_stock_cost=round(ending_stock_cost, 2),
                average_stock_cost=average_stock_cost,
                period_gross_profit=period_gross_profit,
                gmroi_ratio=gmroi_val,
                gmroi_percentage=gmroi_pct,
                daily_sales_qty=round(daily_sales_qty, 2),
                days_of_inventory=days_of_inventory,
                inventory_health=inventory_health,
                revenue_share_pct=rev_share_pct,
                profit_share_pct=prof_share_pct,
                bcg_segment=bcg_segment
            ))

        return scorecards
