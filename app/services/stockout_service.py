from typing import List
from sqlalchemy.orm import Session
from app.models.entities import Product, Store, Inventory, SalesHistory, StoreType, Category
from app.schemas.schemas import (
    WarehouseAvailableStoreOutItem, LostSaleItem, StockoutAnalysisResponse
)

class StockoutService:
    @staticmethod
    def get_stockout_analysis(db: Session) -> StockoutAnalysisResponse:
        stores = db.query(Store).all()
        central_depot = [s for s in stores if s.type == StoreType.CENTRAL_WAREHOUSE.value][0]
        sub_stores = [s for s in stores if s.type == StoreType.STORE.value]

        products = db.query(Product).all()
        
        warehouse_available_store_empty = []
        lost_sales_list = []
        total_estimated_lost_rev = 0.0

        for prod in products:
            # Depo stoğu
            central_inv = db.query(Inventory).filter(
                Inventory.product_id == prod.id,
                Inventory.store_id == central_depot.id
            ).first()
            central_qty = central_inv.quantity_on_hand if central_inv else 0.0

            # Şube stokları
            store_invs = db.query(Inventory).filter(
                Inventory.product_id == prod.id,
                Inventory.store_id.in_([s.id for s in sub_stores])
            ).all()

            out_of_stock_store_names = []
            for st in sub_stores:
                st_inv = next((inv for inv in store_invs if inv.store_id == st.id), None)
                if not st_inv or st_inv.quantity_on_hand <= 0.0:
                    out_of_stock_store_names.append(st.name)

                    # Şubenin geçmiş ortalama satışı
                    st_sales = db.query(SalesHistory).filter(
                        SalesHistory.product_id == prod.id,
                        SalesHistory.store_id == st.id
                    ).all()
                    daily_st_sales = (sum(s.quantity_sold for s in st_sales) / 90.0) if st_sales else 1.0
                    
                    # Son 5 gün stoksuz kalındığı varsayımı
                    oos_days = 5
                    est_lost_qty = round(daily_st_sales * oos_days, 1)
                    est_lost_revenue = round(est_lost_qty * prod.sale_price, 2)
                    total_estimated_lost_rev += est_lost_revenue

                    # Kök Neden Tespiti
                    if central_qty > 50:
                        root_cause = "DEPODA_VAR_SEVKIYAT_YAPILMADI"
                    else:
                        root_cause = "TEDARIKCI_SIPARISI_GECIKTI"

                    lost_sales_list.append(LostSaleItem(
                        product_id=prod.id,
                        barcode=prod.barcode,
                        product_name=prod.name,
                        category_name=prod.category.name if prod.category else "Genel",
                        store_name=st.name,
                        out_of_stock_days=oos_days,
                        daily_lost_quantity=round(daily_st_sales, 1),
                        estimated_lost_revenue=est_lost_revenue,
                        root_cause=root_cause
                    ))

            # Eğer ana depoda mal var ama en az bir şubede 0 stok ise (İkmal Uyuşmazlığı)
            if central_qty > 0 and len(out_of_stock_store_names) > 0:
                recommended_transfer = min(central_qty, len(out_of_stock_store_names) * 20.0)
                warehouse_available_store_empty.append(WarehouseAvailableStoreOutItem(
                    product_id=prod.id,
                    barcode=prod.barcode,
                    product_name=prod.name,
                    category_name=prod.category.name if prod.category else "Genel",
                    central_warehouse_stock=round(central_qty, 1),
                    out_of_stock_stores_count=len(out_of_stock_store_names),
                    out_of_stock_stores=out_of_stock_store_names,
                    recommended_transfer_qty=round(recommended_transfer, 1)
                ))

        return StockoutAnalysisResponse(
            total_estimated_lost_revenue=round(total_estimated_lost_rev, 2),
            gap_count=len(warehouse_available_store_empty),
            warehouse_available_store_empty_items=warehouse_available_store_empty,
            lost_sales_items=lost_sales_list
        )
