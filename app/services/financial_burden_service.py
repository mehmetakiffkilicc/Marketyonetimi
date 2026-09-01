from typing import List
from sqlalchemy.orm import Session
from app.models.entities import Product, Supplier, Category, User, Inventory, SalesHistory
from app.schemas.schemas import (
    CategoryFinancialBurden, BuyerFinancialBurden, SupplierFinancialBurden, FinancialBurdenResponse
)

class FinancialBurdenService:
    @staticmethod
    def get_financial_burden(db: Session) -> FinancialBurdenResponse:
        products = db.query(Product).all()
        prod_map = {p.id: p for p in products}

        inventories = db.query(Inventory).all()
        sales_all = db.query(SalesHistory).all()

        # Toplam Stok Maliyeti
        total_inv_cost = sum(inv.quantity_on_hand * prod_map[inv.product_id].purchase_price for inv in inventories if inv.product_id in prod_map)
        
        # 1. Kategori Bazlı
        categories = db.query(Category).all()
        by_category = []
        for cat in categories:
            cat_prods = [p for p in products if p.category_id == cat.id]
            cat_prod_ids = [p.id for p in cat_prods]
            
            cat_invs = [inv for inv in inventories if inv.product_id in cat_prod_ids]
            cat_cost = sum(inv.quantity_on_hand * prod_map[inv.product_id].purchase_price for inv in cat_invs)
            
            cat_sales = [s for s in sales_all if s.product_id in cat_prod_ids]
            cat_rev = sum(s.gross_revenue for s in cat_sales)
            cat_cogs = sum(s.cogs for s in cat_sales)
            cat_prof = cat_rev - cat_cogs
            
            # Devir gün hesabı
            daily_cogs = (cat_cogs / 90.0) if cat_cogs > 0 else 1.0
            turnover_days = round(cat_cost / daily_cogs, 1)

            share_pct = round((cat_cost / total_inv_cost * 100.0), 2) if total_inv_cost > 0 else 0.0

            by_category.append(CategoryFinancialBurden(
                category_id=cat.id,
                category_name=cat.name,
                stock_cost=round(cat_cost, 2),
                stock_share_pct=share_pct,
                revenue_3m=round(cat_rev, 2),
                profit_3m=round(cat_prof, 2),
                turnover_days=turnover_days
            ))

        # 2. Satın Almacı Bazlı
        buyers = db.query(User).filter(User.role == "SATIN_ALMACI").all()
        by_buyer = []
        total_idle_cost = 0.0

        for b in buyers:
            b_prods = [p for p in products if p.buyer_id == b.id]
            b_prod_ids = [p.id for p in b_prods]

            b_invs = [inv for inv in inventories if inv.product_id in b_prod_ids]
            b_cost = sum(inv.quantity_on_hand * prod_map[inv.product_id].purchase_price for inv in b_invs)

            # Atıl stok hesabı (>45 gün stok)
            b_idle_cost = 0.0
            for p in b_prods:
                p_invs = [inv for inv in b_invs if inv.product_id == p.id]
                p_qty = sum(inv.quantity_on_hand for inv in p_invs)
                p_sales = [s for s in sales_all if s.product_id == p.id]
                p_daily_qty = (sum(s.quantity_sold for s in p_sales) / 90.0) if p_sales else 0.1
                p_days = p_qty / p_daily_qty
                if p_days > 45:
                    # 45 günü aşan kısım atıl stoktur
                    excess_qty = max(0.0, p_qty - (p_daily_qty * 45))
                    b_idle_cost += excess_qty * p.purchase_price

            total_idle_cost += b_idle_cost
            util_pct = round((b_cost / b.monthly_budget_limit * 100.0), 2) if b.monthly_budget_limit > 0 else 0.0

            by_buyer.append(BuyerFinancialBurden(
                buyer_id=b.id,
                buyer_name=b.name,
                category_focus=b.category_focus,
                monthly_budget_limit=b.monthly_budget_limit,
                current_stock_cost=round(b_cost, 2),
                budget_utilization_pct=util_pct,
                idle_stock_cost=round(b_idle_cost, 2)
            ))

        # 3. Üretici Bazlı (Vade Uyumsuzluğu & Nakit Kanaması Tespiti)
        suppliers = db.query(Supplier).all()
        by_supplier = []
        for sup in suppliers:
            s_prods = [p for p in products if p.supplier_id == sup.id]
            s_prod_ids = [p.id for p in s_prods]

            s_invs = [inv for inv in inventories if inv.product_id in s_prod_ids]
            s_cost = sum(inv.quantity_on_hand * prod_map[inv.product_id].purchase_price for inv in s_invs)
            s_qty = sum(inv.quantity_on_hand for inv in s_invs)

            s_sales = [s for s in sales_all if s.product_id in s_prod_ids]
            s_daily_qty = (sum(s.quantity_sold for s in s_sales) / 90.0) if s_sales else 0.1
            s_days = round(s_qty / s_daily_qty, 1)

            # Vade Açığı = Yeter Gün - Ödeme Vadesi
            maturity_gap = round(s_days - sup.payment_term_days, 1)
            risk_status = "HIGH_RISK" if maturity_gap > 10 else "SAFE"

            by_supplier.append(SupplierFinancialBurden(
                supplier_id=sup.id,
                supplier_name=sup.name,
                stock_cost=round(s_cost, 2),
                payment_term_days=sup.payment_term_days,
                days_of_inventory=s_days,
                maturity_gap_days=maturity_gap,
                maturity_risk_status=risk_status
            ))

        return FinancialBurdenResponse(
            total_inventory_cost=round(total_inv_cost, 2),
            total_idle_inventory_cost=round(total_idle_cost, 2),
            by_category=by_category,
            by_buyer=by_buyer,
            by_supplier=by_supplier
        )
