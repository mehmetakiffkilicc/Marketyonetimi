from datetime import date, timedelta
from typing import List, Optional
import io
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from app.models.entities import (
    Product, Supplier, Category, Store, Inventory, SalesHistory,
    Campaign, CampaignProduct, PurchaseOrder, PurchaseOrderItem,
    StoreType, CampaignType, CampaignStatus, POStatus, User
)
from app.schemas.schemas import (
    MonthlySalesHistory, MonthlyForecast, ProductWorkbenchItem,
    PurchasingWorkbenchResponse, CreatePurchaseOrderRequest, PurchaseOrderOut,
    ActivityDetail, PurchaseOrderItemDetailOut, PurchaseOrderReportItem, PurchaseOrdersReportResponse
)

class PurchasingService:
    @staticmethod
    def get_workbench(db: Session, supplier_id: Optional[int] = None, category_id: Optional[int] = None, brand: Optional[str] = None) -> PurchasingWorkbenchResponse:
        query = db.query(Product)
        supplier = None
        category = None

        if supplier_id:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            query = query.filter(Product.supplier_id == supplier_id)
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            query = query.filter(Product.category_id == category_id)
        if brand:
            query = query.filter(Product.brand == brand)

        products = query.all()
        stores = db.query(Store).all()
        central_depot = [s for s in stores if s.type == StoreType.CENTRAL_WAREHOUSE.value][0]

        # Başlık ve Seçim Tipi
        parts = []
        if supplier:
            parts.append(supplier.name)
        if brand:
            parts.append(f"Marka: {brand}")
        if category:
            parts.append(category.name)

        if parts:
            selected_title = " > ".join(parts)
            selection_type = "BRAND_AND_CATEGORY" if len(parts) > 1 else ("BRAND" if supplier or brand else "CATEGORY")
        else:
            selection_type = "ALL"
            selected_title = "Tüm Üreticiler & Markalar"

        target_days = getattr(supplier, "target_days_of_inventory", 21) if supplier else (getattr(category, "target_turnover_days", 21) if category else 21)
        payment_term_days = supplier.payment_term_days if supplier else 45
        lead_time_days = supplier.lead_time_days if supplier else 3

        # Referans tarih: 2026-09-01
        ref_date = date(2026, 9, 1)
        
        # Geçmiş 3 ayın başlangıç ve bitiş tarihleri
        m3_start = date(2026, 6, 1)
        m3_end = date(2026, 6, 30)
        m2_start = date(2026, 7, 1)
        m2_end = date(2026, 7, 31)
        m1_start = date(2026, 8, 1)
        m1_end = date(2026, 8, 31)

        months_ranges = [
            ("Haziran 2026", m3_start, m3_end),
            ("Temmuz 2026", m2_start, m2_end),
            ("Ağustos 2026", m1_start, m1_end)
        ]

        items_response = []
        total_suggested_qty = 0.0
        total_suggested_cost = 0.0

        for prod in products:
            # 1. Stok Durumu
            inventories = db.query(Inventory).filter(Inventory.product_id == prod.id).all()
            central_stock = sum(inv.quantity_on_hand for inv in inventories if inv.store_id == central_depot.id)
            stores_stock = sum(inv.quantity_on_hand for inv in inventories if inv.store_id != central_depot.id)
            total_stock = central_stock + stores_stock
            on_order = sum(inv.quantity_on_order for inv in inventories)

            # 2. Geçmiş 3 Ay Satışları
            past_months_data = []
            total_past_qty = 0.0
            total_past_camp_qty = 0.0

            for m_label, start_d, end_d in months_ranges:
                sales = db.query(SalesHistory).filter(
                    SalesHistory.product_id == prod.id,
                    SalesHistory.sale_date >= start_d,
                    SalesHistory.sale_date <= end_d
                ).all()

                reg_qty = sum(s.quantity_sold for s in sales if not s.was_on_campaign)
                camp_qty = sum(s.quantity_sold for s in sales if s.was_on_campaign)
                m_total_qty = reg_qty + camp_qty
                m_revenue = sum(s.gross_revenue for s in sales)
                m_cogs = sum(s.cogs for s in sales)
                m_profit = m_revenue - m_cogs

                # Aktivite Dönemleri Detayları
                unique_campaign_ids = set(s.campaign_id for s in sales if s.campaign_id)
                activities_list = []
                
                for cid in unique_campaign_ids:
                    camp = db.query(Campaign).filter(Campaign.id == cid).first()
                    if camp:
                        c_sales = [s for s in sales if s.campaign_id == cid]
                        c_qty = sum(s.quantity_sold for s in c_sales)
                        c_rev = sum(s.gross_revenue for s in c_sales)

                        # Ay ismi kısaltma ve periyot formatı
                        m_names = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
                        s_str = f"{camp.start_date.day} {m_names[camp.start_date.month - 1]}"
                        e_str = f"{camp.end_date.day} {m_names[camp.end_date.month - 1]}"
                        period_days = (camp.end_date - camp.start_date).days + 1
                        period_label = f"{s_str} - {e_str} ({period_days} Gün)"

                        # Normal gün satış hızı vs aktivite hızı
                        normal_days = max(1, 30 - period_days)
                        normal_daily_rate = (reg_qty / normal_days) if normal_days > 0 else 1.0
                        camp_daily_rate = (c_qty / period_days) if period_days > 0 else 1.0
                        lift = round(camp_daily_rate / normal_daily_rate, 1) if normal_daily_rate > 0 else 1.0
                        share_pct = round((c_qty / m_total_qty * 100.0), 1) if m_total_qty > 0 else 0.0

                        activities_list.append(ActivityDetail(
                            campaign_id=camp.id,
                            title=camp.title,
                            period_label=period_label,
                            start_date=camp.start_date,
                            end_date=camp.end_date,
                            discount_rate_pct=round(camp.discount_rate * 100.0, 0),
                            activity_sales_qty=round(c_qty, 1),
                            activity_revenue=round(c_rev, 2),
                            activity_share_pct=share_pct,
                            lift_multiplier=lift
                        ))

                past_months_data.append(MonthlySalesHistory(
                    month_label=m_label,
                    regular_quantity=round(reg_qty, 1),
                    campaign_quantity=round(camp_qty, 1),
                    total_quantity=round(m_total_qty, 1),
                    gross_revenue=round(m_revenue, 2),
                    cogs=round(m_cogs, 2),
                    gross_profit=round(m_profit, 2),
                    campaign_count=len(unique_campaign_ids),
                    activities=activities_list
                ))

                total_past_qty += m_total_qty
                total_past_camp_qty += camp_qty

            # 3. Satış Hızı (Son 30 Günlük Run-Rate) & Yeter Gün Sayısı
            last_30_days_sales = past_months_data[-1].total_quantity # Ağustos ayı
            daily_run_rate = max(0.1, last_30_days_sales / 30.0)
            days_of_inventory = round(total_stock / daily_run_rate, 1)

            # Hedef Yeter Gün Sayısına Göre Dinamik Ölçümleme
            target_days = getattr(supplier, "target_days_of_inventory", 21) or 21
            crit_threshold = round(target_days * 0.6, 1)    # Hedefin %60'ından azı Kritik Az
            over_threshold = round(target_days * 1.25, 1)  # Hedefin %125'inden fazlası Fazla Stok

            if days_of_inventory < crit_threshold:
                stock_alert = "CRITICAL_LOW" # Yok satma riski (Hedefin altında)
            elif days_of_inventory > over_threshold:
                stock_alert = "OVERSTOCK"    # Fazla stok riski (Hedefin üstünde)
            else:
                stock_alert = "NORMAL"       # Hedef seviyede / Dengeli

            # 4. Gelecek 3 Ay AI / İstatistiksel Talep Tahmini (Eylül, Ekim, Kasım)
            # Ağırlıklı Ortalama: Ağustos (%50) + Temmuz (%30) + Haziran (%20)
            q_aug = past_months_data[2].total_quantity
            q_jul = past_months_data[1].total_quantity
            q_jun = past_months_data[0].total_quantity
            weighted_base_monthly = (q_aug * 0.5) + (q_jul * 0.3) + (q_jun * 0.2)

            # Mevsimsellik çarpanları (Sonbahar / Okul açılışı etkisi)
            seasonality = {"Eylül 2026": 1.10, "Ekim 2026": 1.05, "Kasım 2026": 1.02}
            
            forecast_data = []
            sum_forecast = 0.0
            for f_month, factor in seasonality.items():
                f_base = round(weighted_base_monthly * factor, 1)
                forecast_data.append(MonthlyForecast(
                    month_label=f_month,
                    base_forecast_qty=f_base,
                    campaign_lift_qty=0.0, # Sipariş anında kampanya eklenirse artar
                    total_forecast_qty=f_base
                ))
                sum_forecast += f_base

            # 5. Önerilen Sipariş Miktarı
            safety_stock_qty = round(daily_run_rate * prod.safety_stock_days, 1)
            gross_needed = sum_forecast + safety_stock_qty
            available_supply = total_stock + on_order
            suggested_qty = max(0.0, round(gross_needed - available_supply))

            total_suggested_qty += suggested_qty
            total_suggested_cost += suggested_qty * prod.purchase_price

            cat_name = prod.category.name if prod.category else "Genel"
            sup_name = prod.supplier.name if prod.supplier else (supplier.name if supplier else "Genel")

            vat_r = getattr(prod, "vat_rate", 0.10) or 0.10
            items_response.append(ProductWorkbenchItem(
                product_id=prod.id,
                barcode=prod.barcode,
                product_name=prod.name,
                brand=prod.brand or "Genel",
                category_name=cat_name,
                supplier_name=sup_name,
                unit=prod.unit,
                purchase_price=prod.purchase_price,
                sale_price=prod.sale_price,
                vat_rate=vat_r,
                central_warehouse_stock=round(central_stock, 1),
                total_stores_stock=round(stores_stock, 1),
                total_network_stock=round(total_stock, 1),
                quantity_on_order=round(on_order, 1),
                daily_run_rate=round(daily_run_rate, 2),
                days_of_inventory=days_of_inventory,
                stock_status_alert=stock_alert,
                past_3_months_sales=past_months_data,
                total_past_3m_qty=round(total_past_qty, 1),
                total_past_3m_campaign_qty=round(total_past_camp_qty, 1),
                forecast_3_months=forecast_data,
                total_forecast_qty=round(sum_forecast, 1),
                safety_stock_qty=safety_stock_qty,
                suggested_order_qty=suggested_qty
            ))

        # Seçim Geneli Ortalama Yeter Gün ve Durum
        mfg_total_stock = sum(it.total_network_stock for it in items_response)
        mfg_daily_sales = sum(it.daily_run_rate for it in items_response)
        actual_avg_days = round(mfg_total_stock / mfg_daily_sales, 1) if mfg_daily_sales > 0 else 0.0

        # KDV Hesaplamaları
        total_suggested_vat = sum(it.suggested_order_qty * it.purchase_price * it.vat_rate for it in items_response)
        total_cost_with_vat = total_suggested_cost + total_suggested_vat

        if actual_avg_days < (target_days * 0.45):
            status_label = "CRITICAL_LOW"
        elif actual_avg_days > (target_days * 1.6):
            status_label = "OVERSTOCK"
        else:
            status_label = "HEALTHY"

        return PurchasingWorkbenchResponse(
            selection_type=selection_type,
            selected_title=selected_title,
            supplier_id=supplier.id if supplier else None,
            supplier_name=supplier.name if supplier else None,
            brand=brand,
            category_id=category.id if category else None,
            category_name=category.name if category else None,
            payment_term_days=payment_term_days,
            lead_time_days=lead_time_days,
            target_days_of_inventory=target_days,
            actual_avg_days_of_inventory=actual_avg_days,
            inventory_status_label=status_label,
            items=items_response,
            summary_total_suggested_qty=round(total_suggested_qty, 1),
            summary_total_suggested_cost=round(total_suggested_cost, 2),
            summary_total_suggested_vat=round(total_suggested_vat, 2),
            summary_total_suggested_cost_with_vat=round(total_cost_with_vat, 2)
        )

    @staticmethod
    def get_brands(db: Session, supplier_id: Optional[int] = None) -> List[str]:
        query = db.query(Product.brand).filter(Product.brand != None)
        if supplier_id:
            query = query.filter(Product.supplier_id == supplier_id)
        brands = [r[0] for r in query.distinct().order_by(Product.brand).all() if r[0]]
        return brands

    @staticmethod
    def get_supplier_workbench(db: Session, supplier_id: int) -> PurchasingWorkbenchResponse:
        return PurchasingService.get_workbench(db, supplier_id=supplier_id)

    @staticmethod
    def create_purchase_order(db: Session, req: CreatePurchaseOrderRequest) -> PurchaseOrderOut:
        supplier = db.query(Supplier).filter(Supplier.id == req.supplier_id).first()
        buyer = db.query(User).filter(User.id == req.buyer_id).first()
        if not supplier or not buyer:
            raise ValueError("Geçersiz tedarikçi veya satın almacı.")

        po_count = db.query(PurchaseOrder).count() + 1
        po_number = f"PO-2026-{po_count:04d}"

        # PO nesnesi
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=supplier.id,
            buyer_id=buyer.id,
            order_date=date.today(),
            expected_delivery_date=req.expected_delivery_date or (date.today() + timedelta(days=supplier.lead_time_days)),
            status=POStatus.APPROVED.value,
            notes=req.notes
        )
        db.add(po)
        db.flush()

        total_po_cost = 0.0
        linked_camp_count = 0

        for item_in in req.items:
            prod = db.query(Product).filter(Product.id == item_in.product_id).first()
            if not prod:
                continue

            item_cost = item_in.ordered_quantity * item_in.unit_cost
            total_po_cost += item_cost

            planned_camp_id = None
            # Eğer sipariş anında kampanya tanımlanmışsa
            if item_in.planned_campaign:
                camp_in = item_in.planned_campaign
                shelf_price = camp_in.shelf_price or prod.sale_price
                promo_price = camp_in.promotional_price or (shelf_price * (1.0 - camp_in.discount_rate))
                target_qty = camp_in.target_sales_qty or item_in.ordered_quantity
                app_channel = camp_in.application_channel or "DİREKT_RAF"
                
                campaign = Campaign(
                    title=camp_in.title,
                    start_date=camp_in.start_date,
                    end_date=camp_in.end_date,
                    campaign_type=camp_in.campaign_type,
                    discount_rate=camp_in.discount_rate,
                    application_channel=app_channel,
                    status=CampaignStatus.PLANNED.value,
                    target_sales_qty=target_qty,
                    target_revenue=camp_in.target_revenue or (target_qty * promo_price),
                    created_from_po_id=po.id,
                    notes=f"Sipariş No {po.po_number} ile oluşturuldu."
                )
                db.add(campaign)
                db.flush()
                
                # Kampanya ürün ilişkisi
                db.add(CampaignProduct(
                    campaign_id=campaign.id,
                    product_id=prod.id,
                    regular_shelf_price=round(shelf_price, 2),
                    promotional_price=round(promo_price, 2),
                    discount_rate=camp_in.discount_rate,
                    target_sales_qty=round(target_qty, 1),
                    application_channel=app_channel
                ))
                planned_camp_id = campaign.id
                linked_camp_count += 1

            # PO Item
            po_item = PurchaseOrderItem(
                po_id=po.id,
                product_id=prod.id,
                suggested_quantity=0.0,
                ordered_quantity=item_in.ordered_quantity,
                unit_cost=item_in.unit_cost,
                planned_campaign_id=planned_camp_id
            )
            db.add(po_item)

            # Depo stoğuna yoldaki sipariş (quantity_on_order) olarak ekle
            central_store = db.query(Store).filter(Store.type == StoreType.CENTRAL_WAREHOUSE.value).first()
            if central_store:
                inv = db.query(Inventory).filter(
                    Inventory.product_id == prod.id,
                    Inventory.store_id == central_store.id
                ).first()
                if inv:
                    inv.quantity_on_order += item_in.ordered_quantity

        po.total_cost = round(total_po_cost, 2)
        db.commit()
        db.refresh(po)

        return PurchaseOrderOut(
            id=po.id,
            po_number=po.po_number,
            supplier_name=supplier.name,
            buyer_name=buyer.name,
            order_date=po.order_date,
            expected_delivery_date=po.expected_delivery_date,
            status=po.status,
            total_cost=po.total_cost,
            item_count=len(req.items),
            linked_campaign_count=linked_camp_count
        )

    @staticmethod
    def get_purchase_orders_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> PurchaseOrdersReportResponse:
        query = db.query(PurchaseOrder)

        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)
        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        if status:
            query = query.filter(PurchaseOrder.status == status)

        pos = query.order_by(PurchaseOrder.order_date.desc()).all()
        ref_date = date(2026, 9, 1)

        orders_out = []
        grand_qty = 0.0
        grand_net = 0.0
        grand_vat = 0.0
        grand_with_vat = 0.0
        upcoming_30d_amount = 0.0
        terms_sum = 0
        valid_terms_count = 0

        for po in pos:
            sup = po.supplier
            buyer = po.buyer
            term_days = sup.payment_term_days if sup else 45
            lead_days = sup.lead_time_days if sup else 3

            delivery_d = po.expected_delivery_date or (po.order_date + timedelta(days=lead_days))
            due_date = delivery_d + timedelta(days=term_days)
            days_left = (due_date - ref_date).days

            terms_sum += term_days
            valid_terms_count += 1

            # Kalem detayları
            items_out = []
            po_net = 0.0
            po_vat = 0.0
            po_qty = 0.0

            for pi in po.items:
                p = pi.product
                if not p:
                    continue
                q = pi.ordered_quantity
                c = pi.unit_cost
                vat_r = getattr(p, "vat_rate", 0.10) or 0.10
                
                net_line = q * c
                vat_line = net_line * vat_r
                with_vat_line = net_line + vat_line

                po_qty += q
                po_net += net_line
                po_vat += vat_line

                camp_title = None
                if pi.planned_campaign_id:
                    c_obj = db.query(Campaign).filter(Campaign.id == pi.planned_campaign_id).first()
                    if c_obj:
                        camp_title = c_obj.title

                # Sipariş Öncesi Stok ve Yeter Gün Sayısı
                invs = db.query(Inventory).filter(Inventory.product_id == p.id).all()
                cur_stock = sum(inv.quantity_on_hand for inv in invs) if invs else 0.0

                cutoff_90d = date(2026, 6, 1)
                sales_recs = db.query(SalesHistory).filter(
                    SalesHistory.product_id == p.id,
                    SalesHistory.sale_date >= cutoff_90d
                ).all()
                total_sales_90d = sum(s.quantity_sold for s in sales_recs) if sales_recs else 0.0
                daily_sales = round(total_sales_90d / 90.0, 2) if total_sales_90d > 0 else max(1.0, round(q / 30.0, 2))
                days_of_inv = round(cur_stock / daily_sales, 1) if daily_sales > 0 else 0.0

                items_out.append(PurchaseOrderItemDetailOut(
                    product_id=p.id,
                    barcode=p.barcode,
                    product_name=p.name,
                    brand=p.brand or "Genel",
                    category_name=p.category.name if p.category else "Genel",
                    stock_before_order=round(cur_stock, 1),
                    days_of_inventory_before_order=days_of_inv,
                    daily_sales=daily_sales,
                    ordered_quantity=round(q, 1),
                    unit=p.unit,
                    unit_cost=round(c, 2),
                    vat_rate=vat_r,
                    line_total_net=round(net_line, 2),
                    line_total_vat=round(vat_line, 2),
                    line_total_with_vat=round(with_vat_line, 2),
                    planned_campaign_title=camp_title
                ))

            po_with_vat = po_net + po_vat
            grand_qty += po_qty
            grand_net += po_net
            grand_vat += po_vat
            grand_with_vat += po_with_vat

            # 30 gün içinde vadesi gelen tutar
            if 0 <= days_left <= 30:
                upcoming_30d_amount += po_with_vat

            linked_camps = len(po.linked_campaigns) if po.linked_campaigns else 0

            orders_out.append(PurchaseOrderReportItem(
                id=po.id,
                po_number=po.po_number,
                order_date=po.order_date,
                supplier_id=sup.id if sup else 0,
                supplier_name=sup.name if sup else "Genel",
                buyer_name=buyer.name if buyer else "Satın Alma",
                payment_term_days=term_days,
                expected_delivery_date=delivery_d,
                estimated_payment_due_date=due_date,
                days_until_payment=days_left,
                status=po.status,
                total_quantity=round(po_qty, 1),
                item_count=len(po.items),
                total_cost_net=round(po_net, 2),
                total_vat=round(po_vat, 2),
                total_cost_with_vat=round(po_with_vat, 2),
                notes=po.notes,
                linked_campaign_count=linked_camps,
                items=items_out
            ))

        avg_term = round(terms_sum / valid_terms_count, 1) if valid_terms_count > 0 else 45.0

        return PurchaseOrdersReportResponse(
            start_date=start_date,
            end_date=end_date,
            total_po_count=len(pos),
            total_ordered_quantity=round(grand_qty, 1),
            total_amount_net=round(grand_net, 2),
            total_vat=round(grand_vat, 2),
            total_amount_with_vat=round(grand_with_vat, 2),
            upcoming_30d_payment_amount=round(upcoming_30d_amount, 2),
            avg_payment_term_days=avg_term,
            orders=orders_out
        )

    @staticmethod
    def export_purchase_orders_to_excel(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None,
        buyer_name: Optional[str] = None,
        due_status: Optional[str] = None,
        search: Optional[str] = None,
        po_ids: Optional[List[int]] = None
    ) -> io.BytesIO:
        report = PurchasingService.get_purchase_orders_report(
            db, start_date=start_date, end_date=end_date, supplier_id=supplier_id, status=status
        )

        filtered_orders = report.orders

        # 1. po_ids filter (Exact filtered list from UI)
        if po_ids is not None and len(po_ids) > 0:
            filtered_orders = [po for po in filtered_orders if po.id in po_ids]

        # 2. Buyer filter
        if buyer_name:
            filtered_orders = [po for po in filtered_orders if po.buyer_name == buyer_name]

        # 3. Due Status filter
        if due_status:
            if due_status == "OVERDUE":
                filtered_orders = [po for po in filtered_orders if po.days_until_payment < 0]
            elif due_status == "CRITICAL_15":
                filtered_orders = [po for po in filtered_orders if 0 <= po.days_until_payment <= 15]
            elif due_status == "MEDIUM_30":
                filtered_orders = [po for po in filtered_orders if 15 < po.days_until_payment <= 30]
            elif due_status == "FUTURE":
                filtered_orders = [po for po in filtered_orders if po.days_until_payment > 30]

        # 4. Keyword search
        if search:
            q = search.lower().strip()
            filtered_orders = [
                po for po in filtered_orders
                if q in po.po_number.lower() or 
                   q in po.supplier_name.lower() or 
                   q in po.buyer_name.lower() or 
                   (po.notes and q in po.notes.lower()) or 
                   any(q in it.product_name.lower() or q in it.barcode.lower() or q in it.brand.lower() for it in po.items)
            ]

        # Sheet 1: Detailed Items
        rows_items = []
        # Sheet 2: PO Summary Matrix
        rows_summary = []

        for po in filtered_orders:
            due_label = "Vadesi Geçti" if po.days_until_payment < 0 else f"{po.days_until_payment} Gün Kaldı"
            
            rows_summary.append({
                "Sipariş No": po.po_number,
                "Sipariş Tarihi": po.order_date.strftime("%d.%m.%Y"),
                "Üretici Firma": po.supplier_name,
                "Satın Almacı": po.buyer_name,
                "Teslim Tarihi": po.expected_delivery_date.strftime("%d.%m.%Y"),
                "Ödeme Vadesi (Gün)": po.payment_term_days,
                "Yaklaşık Ödeme Tarihi (Vade)": po.estimated_payment_due_date.strftime("%d.%m.%Y"),
                "Vade Durumu": due_label,
                "Kalan Gün": po.days_until_payment,
                "Kalem Çeşidi": po.item_count,
                "Toplam Sipariş Adedi": po.total_quantity,
                "Net Tutar (TL)": po.total_cost_net,
                "KDV Tutarı (TL)": po.total_vat,
                "KDV Dahil Toplam (TL)": po.total_cost_with_vat,
                "Sipariş Durumu": po.status,
                "Sipariş Notu": po.notes or "-"
            })

            for it in po.items:
                rows_items.append({
                    "Sipariş No": po.po_number,
                    "Sipariş Tarihi": po.order_date.strftime("%d.%m.%Y"),
                    "Üretici Firma": po.supplier_name,
                    "Satın Almacı": po.buyer_name,
                    "Teslim Tarihi": po.expected_delivery_date.strftime("%d.%m.%Y"),
                    "Ödeme Vadesi (Gün)": po.payment_term_days,
                    "Yaklaşık Ödeme Tarihi": po.estimated_payment_due_date.strftime("%d.%m.%Y"),
                    "Vade Durumu": due_label,
                    "Barkod": it.barcode,
                    "Marka": it.brand,
                    "Ürün Adı": it.product_name,
                    "Kategori": it.category_name,
                    "Sipariş Öncesi Stok": it.stock_before_order,
                    "Sipariş Öncesi Yeter Gün": it.days_of_inventory_before_order,
                    "Günlük Satış Hızı": it.daily_sales,
                    "Sipariş Adedi": it.ordered_quantity,
                    "Birim": it.unit,
                    "Birim Alış Fiyatı (TL)": it.unit_cost,
                    "KDV Oranı (%)": round(it.vat_rate * 100, 0),
                    "Satır Net Tutar (TL)": it.line_total_net,
                    "KDV Tutarı (TL)": it.line_total_vat,
                    "Satır Toplam (KDV Dahil TL)": it.line_total_with_vat,
                    "Bağlı Kampanya": it.planned_campaign_title or "-",
                    "Sipariş Durumu": po.status
                })

        df_items = pd.DataFrame(rows_items)
        df_summary = pd.DataFrame(rows_summary)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Siparis_Vade_Ozeti', index=False)
            df_items.to_excel(writer, sheet_name='Siparis_Kalemleri_Detayli', index=False)
        output.seek(0)
        return output
