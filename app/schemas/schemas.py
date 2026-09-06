from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

# --- Base Entity Schemas ---
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    category_focus: Optional[str] = None
    monthly_budget_limit: float

    class Config:
        from_attributes = True

class SupplierOut(BaseModel):
    id: int
    name: str
    code: str
    payment_term_days: int
    lead_time_days: int
    target_days_of_inventory: int = 21
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    min_order_amount: float

    class Config:
        from_attributes = True

class UpdateSupplierTargetDaysRequest(BaseModel):
    target_days_of_inventory: int

class CategoryOut(BaseModel):
    id: int
    name: str
    code: str
    parent_id: Optional[int] = None
    target_margin_pct: float
    target_turnover_days: int

    class Config:
        from_attributes = True

class ProductOut(BaseModel):
    id: int
    barcode: str
    name: str
    category_id: int
    category_name: Optional[str] = None
    supplier_id: int
    supplier_name: Optional[str] = None
    unit: str
    purchase_price: float
    sale_price: float
    vat_rate: float
    shelf_life_days: int
    safety_stock_days: int

    class Config:
        from_attributes = True

class UpdateSupplierParametersRequest(BaseModel):
    target_days_of_inventory: Optional[float] = None
    lead_time_days: Optional[int] = None
    payment_term_days: Optional[int] = None
    min_order_amount: Optional[float] = None

class SupplierProductDetailItem(BaseModel):
    id: int
    barcode: str
    name: str
    brand: Optional[str] = None
    category_id: int
    category_name: str
    unit: str
    purchase_price: float
    sale_price: float
    safety_stock_days: int
    total_stock_qty: float
    total_stock_cost: float
    daily_sales_rate: float
    days_of_inventory: float

class SupplierDetailResponse(BaseModel):
    id: int
    name: str
    code: str
    payment_term_days: int
    lead_time_days: int
    target_days_of_inventory: float
    min_order_amount: float
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    total_stock_cost: float
    total_revenue_3m: float
    total_profit_3m: float
    gmroi_ratio: float
    products: List[SupplierProductDetailItem]

class UpdateProductParametersRequest(BaseModel):
    safety_stock_days: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None

class StoreOut(BaseModel):
    id: int
    name: str
    code: str
    type: str
    city: str
    district: Optional[str] = None
    sqm_area: float

    class Config:
        from_attributes = True

# --- Purchasing & Workbench Schemas ---

class ActivityDetail(BaseModel):
    campaign_id: int
    title: str
    period_label: str          # Örn: "10-18 Tem (9 Gün)"
    start_date: date
    end_date: date
    discount_rate_pct: float   # Örn: 15.0 (%)
    activity_sales_qty: float  # Aktivite dönemindeki fiili satış adedi
    activity_revenue: float    # Aktivite dönemindeki ciro
    activity_share_pct: float  # O ayki toplam satıştaki payı %
    lift_multiplier: float     # Normal güne kıyasla kaç katı sattı (örn: 2.4x)

class MonthlySalesHistory(BaseModel):
    month_label: str           # Örn: "Haziran 2026", "Temmuz 2026", "Ağustos 2026"
    regular_quantity: float
    campaign_quantity: float
    total_quantity: float
    gross_revenue: float
    cogs: float
    gross_profit: float
    campaign_count: int
    activities: List[ActivityDetail] = []

class MonthlyForecast(BaseModel):
    month_label: str       # Örn: "Eylül 2026", "Ekim 2026", "Kasım 2026"
    base_forecast_qty: float
    campaign_lift_qty: float
    total_forecast_qty: float

class ProductWorkbenchItem(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    brand: Optional[str] = "Genel" # Marka (Örn: Bingo, Papia, Familia, Molfix, Domestos, Ariel)
    category_name: str
    supplier_name: str
    unit: str
    purchase_price: float
    sale_price: float
    vat_rate: float = 0.10 # KDV oranı (Örn: 0.10, 0.20, 0.01)
    
    # Anlık Stok
    central_warehouse_stock: float
    total_stores_stock: float
    total_network_stock: float
    quantity_on_order: float # Yoldaki sipariş
    
    # Satış Hızı & Yeter Gün
    daily_run_rate: float
    days_of_inventory: float # Yeter gün
    stock_status_alert: str # "CRITICAL_LOW", "NORMAL", "OVERSTOCK"
    
    # Geçmiş 3 Ay Satışlar
    past_3_months_sales: List[MonthlySalesHistory]
    total_past_3m_qty: float
    total_past_3m_campaign_qty: float
    
    # Gelecek 3 Ay AI Tahmini
    forecast_3_months: List[MonthlyForecast]
    total_forecast_qty: float
    
    # Önerilen Sipariş
    safety_stock_qty: float
    suggested_order_qty: float

class PurchasingWorkbenchResponse(BaseModel):
    selection_type: str = "BRAND" # BRAND, CATEGORY, BRAND_AND_CATEGORY, ALL
    selected_title: str = ""
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    payment_term_days: int = 45
    lead_time_days: int = 3
    target_days_of_inventory: int = 21
    actual_avg_days_of_inventory: float = 0.0
    inventory_status_label: str = "NORMAL"
    items: List[ProductWorkbenchItem]
    summary_total_suggested_qty: float
    summary_total_suggested_cost: float
    summary_total_suggested_vat: float = 0.0
    summary_total_suggested_cost_with_vat: float = 0.0

class CampaignPlanInput(BaseModel):
    title: str
    start_date: date
    end_date: date
    campaign_type: str = "PERCENT_DISCOUNT" # PERCENT_DISCOUNT, BUY_X_PAY_Y, SECOND_DISCOUNT, BASKET_DISCOUNT
    discount_rate: float = 0.15             # %15
    shelf_price: Optional[float] = None
    promotional_price: Optional[float] = None
    target_sales_qty: float = 0.0
    target_revenue: float = 0.0
    application_channel: str = "DİREKT_RAF" # DİREKT_RAF, DİJİTAL_KART, HER_İKİSİ

class SingleProductCampaignCreateRequest(BaseModel):
    product_id: int
    title: str
    start_date: date
    end_date: date
    campaign_type: str = "PERCENT_DISCOUNT"
    discount_rate: float = 0.15
    shelf_price: Optional[float] = None
    promotional_price: Optional[float] = None
    target_sales_qty: float = 0.0
    application_channel: str = "DİREKT_RAF"
    notes: Optional[str] = None

class PurchaseOrderItemInput(BaseModel):
    product_id: int
    ordered_quantity: float
    unit_cost: float
    planned_campaign: Optional[CampaignPlanInput] = None

class CreatePurchaseOrderRequest(BaseModel):
    supplier_id: int
    buyer_id: int
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[PurchaseOrderItemInput]

class PurchaseOrderOut(BaseModel):
    id: int
    po_number: str
    supplier_name: str
    buyer_name: str
    order_date: date
    expected_delivery_date: Optional[date] = None
    status: str
    total_cost: float
    item_count: int
    linked_campaign_count: int

class PurchaseOrdersExportFilterRequest(BaseModel):
    po_ids: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    supplier_id: Optional[int] = None
    buyer_name: Optional[str] = None
    status: Optional[str] = None
    due_status: Optional[str] = None
    search: Optional[str] = None

# --- Verilen Siparişler & Finansal Vade / Nakit Akış Raporu Şemaları ---

class PurchaseOrderItemDetailOut(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    brand: str
    category_name: str
    stock_before_order: float = 0.0
    days_of_inventory_before_order: float = 0.0
    daily_sales: float = 0.0
    ordered_quantity: float
    unit: str
    unit_cost: float
    vat_rate: float
    line_total_net: float
    line_total_vat: float
    line_total_with_vat: float
    planned_campaign_title: Optional[str] = None

class PurchaseOrderReportItem(BaseModel):
    id: int
    po_number: str
    order_date: date
    supplier_id: int
    supplier_name: str
    buyer_name: str
    payment_term_days: int
    expected_delivery_date: date
    estimated_payment_due_date: date # Teslimden itibaren yaklaşık ödeme tarihi
    days_until_payment: int          # Ödemeye kalan gün sayısı (Negatif ise geçmiş)
    status: str                      # DRAFT, APPROVED, SENT, RECEIVED, COMPLETED
    total_quantity: float
    item_count: int
    total_cost_net: float            # KDV Hariç
    total_vat: float                 # KDV Tutarı
    total_cost_with_vat: float       # KDV Dahil
    notes: Optional[str] = None
    linked_campaign_count: int
    items: List[PurchaseOrderItemDetailOut] = []

class PurchaseOrdersReportResponse(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_po_count: int
    total_ordered_quantity: float
    total_amount_net: float
    total_vat: float
    total_amount_with_vat: float
    upcoming_30d_payment_amount: float # 30 gün içinde vadesi gelen tutar
    avg_payment_term_days: float
    orders: List[PurchaseOrderReportItem]

# --- Supplier Performance Schemas ---

class SupplierScorecardItem(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_code: str
    payment_term_days: int
    lead_time_days: int
    target_days_of_inventory: float = 21.0
    
    # Stok Metrikleri
    total_stock_qty: float
    total_stock_cost: float
    
    # Satış & Kârlılık Metrikleri (Son 3 Ay)
    total_sales_qty: float
    total_revenue: float
    total_cogs: float
    gross_profit: float
    # GMROI & Stok Maliyet Ayrışımı (Dönem Başı / Dönem Sonu / Ortalama Stok / Kârlılık)
    beginning_stock_cost: float = 0.0 # Dönem Başı Stok Maliyeti (TL)
    ending_stock_cost: float = 0.0    # Dönem Sonu Stok Maliyeti (TL)
    average_stock_cost: float = 0.0   # Ortalama Stok Maliyeti (TL) = (D.Başı + D.Sonu) / 2
    period_gross_profit: float = 0.0  # Dönem Toplam Brüt Kârlılık (TL)
    gmroi_ratio: float = 0.0          # GMROI Oranı (Örn: 5.97x)
    gmroi_percentage: float = 0.0     # GMROI Yüzdesi (Örn: %597)
    
    # Yeter Gün & Hız
    daily_sales_qty: float
    days_of_inventory: float # Yeter gün sayısı (Fiili Ortalama)
    inventory_health: str    # "CRITICAL_LOW", "HEALTHY", "OVERSTOCK"
    
    # Ciro ve Kâr Payı
    revenue_share_pct: float # Market toplam cirosundaki payı
    profit_share_pct: float  # Market toplam kârındaki payı
    bcg_segment: str         # "YILDIZ" (Yüksek Ciro - Yüksek Kâr), "NAKİT İNEĞİ" (Yüksek Ciro - Düşük Kâr), "SORU İŞARETİ" (Düşük Ciro - Yüksek Kâr), "DÜŞÜK PERFORMANS"

# --- Financial Burden Schemas ---

class CategoryFinancialBurden(BaseModel):
    category_id: int
    category_name: str
    stock_cost: float
    stock_share_pct: float
    revenue_3m: float
    profit_3m: float
    turnover_days: float

class BuyerFinancialBurden(BaseModel):
    buyer_id: int
    buyer_name: str
    category_focus: Optional[str]
    monthly_budget_limit: float
    current_stock_cost: float
    budget_utilization_pct: float
    idle_stock_cost: float # 45 günden fazla yeter günü olan stok maliyeti

class SupplierFinancialBurden(BaseModel):
    supplier_id: int
    supplier_name: str
    stock_cost: float
    payment_term_days: int
    days_of_inventory: float
    maturity_gap_days: float # Yeter gün - Vade (Pozitifse nakit kanaması)
    maturity_risk_status: str # "SAFE", "HIGH_RISK"

class FinancialBurdenResponse(BaseModel):
    total_inventory_cost: float
    total_idle_inventory_cost: float
    by_category: List[CategoryFinancialBurden]
    by_buyer: List[BuyerFinancialBurden]
    by_supplier: List[SupplierFinancialBurden]

# --- Stockout & Distribution Gap Schemas ---

class WarehouseAvailableStoreOutItem(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    category_name: str
    central_warehouse_stock: float
    out_of_stock_stores_count: int
    out_of_stock_stores: List[str]
    recommended_transfer_qty: float

class LostSaleItem(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    category_name: str
    store_name: str
    out_of_stock_days: int
    daily_lost_quantity: float
    estimated_lost_revenue: float
    root_cause: str # "WAREHOUSE_AVAILABLE_NOT_DISPATCHED", "SUPPLIER_NOT_ORDERED", "SUPPLIER_DELAY"

class StockoutAnalysisResponse(BaseModel):
    total_estimated_lost_revenue: float
    gap_count: int
    warehouse_available_store_empty_items: List[WarehouseAvailableStoreOutItem]
    lost_sales_items: List[LostSaleItem]

# --- Campaign Lifecycle Schemas ---

class CampaignProductItemOut(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    category_name: str
    supplier_name: str
    regular_shelf_price: float
    promotional_price: float
    discount_rate_pct: float
    target_sales_qty: float
    application_channel: str

class CampaignReportItem(BaseModel):
    id: int
    title: str
    start_date: date
    end_date: date
    campaign_type: str
    discount_rate: float
    application_channel: str = "DİREKT_RAF"
    status: str
    target_sales_qty: float
    target_revenue: float
    actual_sales_qty: float
    actual_revenue: float
    achievement_rate_pct: float
    leftover_stock_qty: float
    created_from_po_number: Optional[str] = None
    products: List[CampaignProductItemOut] = []

# --- Store Inventory Health & Stock Classification Schemas (Yetersiz, Atıl, Ölü Stok) ---

class StoreProductStockHealthItem(BaseModel):
    id: int
    store_id: int
    store_name: str
    store_type: str # CENTRAL_WAREHOUSE or STORE
    product_id: int
    barcode: str
    product_name: str
    brand: str
    category_id: int
    category_name: str
    supplier_id: int
    supplier_name: str
    buyer_id: Optional[int] = None
    buyer_name: str
    unit: str
    purchase_price: float
    sale_price: float
    current_stock_qty: float
    current_stock_cost: float
    daily_sales_rate: float
    days_of_inventory: float
    sales_30d_qty: float
    sales_90d_qty: float
    stock_health_status: str # "CRITICAL_LOW" (Yetersiz Stok), "OVERSTOCK" (Atıl Stok), "DEAD_STOCK" (Ölü Stok), "HEALTHY" (Sağlıklı)
    health_status_label: str # "Yetersiz Stok", "Atıl Stok (>45g)", "Ölü Stok (Hareketsiz)", "Sağlıklı Stok"
    action_recommendation: str # "Sipariş Ver", "İndirim / Kampanya Yap", "Depodan Şubeye Sevk Et", "Tedarikçiye İade", "Normal İzleme"

class StoreInventoryHealthSummary(BaseModel):
    total_products_count: int
    total_stock_qty: float
    total_stock_cost: float
    
    # 4 Temel Stok Sağlık Grubu Özeti
    critical_stock_count: int
    critical_stock_cost: float
    
    overstock_count: int
    overstock_cost: float
    
    dead_stock_count: int
    dead_stock_cost: float
    
    healthy_stock_count: int
    healthy_stock_cost: float
    
    avg_days_of_inventory: float
    items: List[StoreProductStockHealthItem]

class StoreStockHealthExportFilterRequest(BaseModel):
    store_id: Optional[int] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    brand: Optional[str] = None
    buyer_id: Optional[int] = None
    health_status: Optional[str] = None
    search: Optional[str] = None
    item_ids: Optional[List[int]] = None

# --- Executive (Patron) Dashboard Schemas ---

class ExecutiveSubBreakdownItem(BaseModel):
    id: int
    name: str
    product_count: int
    revenue_3m: float
    cogs_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    stock_qty: float
    stock_share_pct: float = 0.0
    gmroi_ratio: float

class ExecutiveProductSubItem(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    category_name: str
    supplier_name: str
    store_name: Optional[str] = None
    sale_price: float
    purchase_price: float
    stock_qty: float
    stock_cost: float
    revenue_3m: float
    profit_3m: float
    days_of_inventory: float
    health_status: str

class StorePerformanceItem(BaseModel):
    store_id: int
    store_name: str
    store_type: str
    city: str
    district: Optional[str] = None
    revenue_3m: float
    cogs_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    stock_qty: float
    stock_share_pct: float = 0.0
    days_of_inventory: float
    gmroi_ratio: float
    critical_stock_count: int
    categories_breakdown: List[ExecutiveSubBreakdownItem] = []
    suppliers_breakdown: List[ExecutiveSubBreakdownItem] = []
    products: List[ExecutiveProductSubItem] = []

class CategoryPerformanceItem(BaseModel):
    category_id: int
    category_name: str
    revenue_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    stock_share_pct: float = 0.0
    gmroi_ratio: float
    revenue_share_pct: float
    days_of_inventory: float = 0.0

class ExecutiveTopRiskItem(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    category_name: str
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    store_name: str
    current_stock: float
    daily_sales: float
    lost_revenue_potential: float
    risk_type: str # "STOCKOUT", "DEAD_STOCK", "OVERSTOCK"
    action_label: str

class ExecutiveSupplierRiskGroup(BaseModel):
    supplier_id: int
    supplier_name: str
    total_amount: float
    total_qty: float
    item_count: int
    items: List[ExecutiveTopRiskItem]

class ExecutiveUrgentPaymentItem(BaseModel):
    po_id: int
    po_number: str
    supplier_name: str
    order_date: date
    due_date: date
    days_left: int
    amount_with_vat: float
    status: str

class ExecutiveStarSupplierItem(BaseModel):
    supplier_id: int
    supplier_name: str
    revenue: float
    profit: float
    revenue_share_pct: float
    profit_share_pct: float
    gmroi_ratio: float
    bcg_segment: str

class BuyerCategorySubItem(BaseModel):
    category_id: int
    category_name: str
    product_count: int
    revenue_3m: float
    cogs_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    stock_qty: float
    gmroi_ratio: float

class BuyerSupplierSubItem(BaseModel):
    supplier_id: int
    supplier_name: str
    product_count: int
    revenue_3m: float
    cogs_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    stock_qty: float
    gmroi_ratio: float

class BuyerProductSubItem(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    category_name: str
    supplier_id: int
    supplier_name: str
    sale_price: float
    purchase_price: float
    stock_qty: float
    stock_cost: float
    revenue_3m: float
    profit_3m: float
    days_of_inventory: float
    health_status: str

class BuyerPerformanceItem(BaseModel):
    buyer_id: int
    buyer_name: str
    role: str
    category_focus: str
    monthly_budget_limit: float
    managed_products_count: int
    revenue_3m: float
    cogs_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    idle_stock_cost: float
    budget_utilization_pct: float
    gmroi_ratio: float
    days_of_inventory: float
    critical_stock_count: int
    categories_breakdown: List[BuyerCategorySubItem] = []
    suppliers_breakdown: List[BuyerSupplierSubItem] = []
    products: List[BuyerProductSubItem] = []

class SupplierExecutiveItem(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_code: str
    payment_term_days: int
    lead_time_days: int
    target_days_of_inventory: float
    days_of_inventory: float
    revenue_3m: float
    profit_3m: float
    margin_pct: float
    stock_cost: float
    average_stock_cost: float
    gmroi_ratio: float
    revenue_share_pct: float
    profit_share_pct: float
    stock_share_pct: float = 0.0
    bcg_segment: str
    upcoming_payment_due: float
    overdue_payment_due: float
    product_count: int
    stores_breakdown: List[ExecutiveSubBreakdownItem] = []
    categories_breakdown: List[ExecutiveSubBreakdownItem] = []
    products: List[ExecutiveProductSubItem] = []

class ExecutiveDashboardSummary(BaseModel):
    total_network_revenue: float
    total_network_cogs: float
    total_network_profit: float
    network_margin_pct: float
    
    total_inventory_cost: float
    total_inventory_qty: float
    overall_gmroi: float
    avg_days_of_inventory: float
    
    upcoming_30d_payment_due: float
    overdue_payment_due: float
    
    total_active_campaigns_count: int
    total_campaign_revenue: float
    
    # 🆕 Patron Kokpiti (Executive Metrics)
    prior_year_revenue: float = 0.0
    prior_year_qty: float = 0.0
    current_year_qty: float = 0.0
    revenue_growth_nominal_pct: float = 0.0
    qty_growth_pct: float = 0.0
    food_inflation_rate_pct: float = 36.4
    real_growth_pct: float = 0.0
    sector_growth_rate_pct: float = 38.2
    market_share_diff_pct: float = 0.0
    
    total_staff_count: int = 84
    revenue_per_staff: float = 0.0
    prior_revenue_per_staff: float = 0.0
    revenue_per_sqm: float = 0.0
    total_sales_area_sqm: float = 2450.0
    
    total_customer_count: int = 0
    prior_customer_count: int = 0
    avg_basket_amount: float = 0.0
    prior_avg_basket_amount: float = 0.0
    avg_basket_items_count: float = 5.2
    
    target_gross_profit: float = 0.0
    target_margin_pct: float = 28.0
    gross_profit_variance_try: float = 0.0
    target_network_ygs: float = 14.0
    excess_inventory_cost: float = 0.0
    
    ygs_category_comparison: List[Dict[str, Any]] = []
    gmroi_by_buyer: List[Dict[str, Any]] = []
    gmroi_by_category: List[Dict[str, Any]] = []
    gmroi_by_supplier: List[Dict[str, Any]] = []
    space_to_sales_categories: List[Dict[str, Any]] = []
    executive_ai_insights: List[Dict[str, Any]] = []
    
    # 🆕 Karşılaştırmalı Performans Matrisleri
    stores_comparison: List[Dict[str, Any]] = []
    categories_comparison: List[Dict[str, Any]] = []
    suppliers_comparison: List[Dict[str, Any]] = []
    buyers_comparison: List[Dict[str, Any]] = []
    
    stores_performance: List[StorePerformanceItem]
    categories_performance: List[CategoryPerformanceItem]
    buyers_performance: List[BuyerPerformanceItem] = []
    suppliers_breakdown: List[SupplierExecutiveItem] = []
    top_stockout_risks: List[ExecutiveTopRiskItem]
    top_dead_stocks: List[ExecutiveTopRiskItem]
    stockout_by_supplier: List[ExecutiveSupplierRiskGroup] = []
    dead_stock_by_supplier: List[ExecutiveSupplierRiskGroup] = []
    top_urgent_payments: List[ExecutiveUrgentPaymentItem]
    top_star_suppliers: List[ExecutiveStarSupplierItem]

# --- Action Cards & Trigger Schemas ---

class ActionCardCreate(BaseModel):
    source_module: str
    title: str
    description: Optional[str] = None
    root_cause: Optional[str] = None
    financial_impact_try: float = 0.0
    assigned_to: Optional[str] = None
    approver: Optional[str] = None
    priority: str = "MEDIUM"
    deadline_date: Optional[date] = None

class ActionCardResolveRequest(BaseModel):
    resolution_evidence: str
    actual_recovered_try: float = 0.0

class ActionCardOut(BaseModel):
    id: int
    card_code: str
    source_module: str
    title: str
    description: Optional[str] = None
    root_cause: Optional[str] = None
    financial_impact_try: float
    actual_recovered_try: float
    assigned_to: Optional[str] = None
    approver: Optional[str] = None
    priority: str
    status: str
    deadline_date: Optional[date] = None
    resolution_evidence: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- XPlusCRM Integration Schemas ---

class StoreLocationDto(BaseModel):
    latitude: float
    longitude: float
    target_radius_km: float = 5.0

class CRMOverstockLiquidationPayload(BaseModel):
    event_id: str
    event_type: str = "INVENTORY_OVERSTOCK_ALERT"
    timestamp: datetime
    store_id: str
    store_location: Optional[StoreLocationDto] = None
    sku: str
    product_name: str
    category_code: str
    excess_stock_units: float
    current_shelf_price: float
    max_allowed_discount_pct: float
    suggested_promo_price: float
    target_customer_count: int
    campaign_deadline: Optional[datetime] = None

class CRMCampaignFeedbackPayload(BaseModel):
    campaign_id: str
    origin_event_id: Optional[str] = None
    targeted_customers: int = 0
    messages_delivered: int = 0
    coupons_redeemed_in_store: int = 0
    conversion_rate_pct: float = 0.0
    total_revenue_generated_try: float = 0.0
    units_sold: int = 0
    remaining_excess_units: int = 0
    incremental_basket_revenue_try: float = 0.0
    dominant_segment: Optional[str] = None
    avg_total_basket_value_try: float = 0.0
    churn_prevented_customer_count: int = 0

class CRMSimulationRequest(BaseModel):
    store_id: int
    product_id: int
    max_discount_pct: float = 20.0

class CRMSimulationResponse(BaseModel):
    product_id: int
    product_name: str
    store_id: int
    store_name: str
    excess_stock_qty: float
    current_sale_price: float
    suggested_promo_price: float
    discount_pct: float
    estimated_target_customers: int
    estimated_conversion_rate_pct: float
    estimated_revenue_try: float
    estimated_basket_lift_try: float
    estimated_liquidation_days: int

class CRMCampaignInsightItem(BaseModel):
    id: int
    campaign_id: str
    origin_event_id: Optional[str] = None
    targeted_customers: int
    coupons_redeemed: int
    conversion_rate_pct: float
    total_revenue_try: float
    units_sold: int
    incremental_basket_revenue_try: float
    dominant_segment: Optional[str] = None
    avg_total_basket_value_try: float
    churn_prevented_customer_count: int
    received_at: datetime

    class Config:
        from_attributes = True

# --- Perakende Kariyer Akademisi (HR Skills) Integration Schemas ---

class SkillDeltaDto(BaseModel):
    competency_area: str
    previous_score: float
    new_score: float
    unlocked_operational_role: Optional[str] = None

class SkillVerificationPayload(BaseModel):
    certification_event_id: str
    employee_code: str
    course_code: str
    course_name: str
    completion_date: Optional[datetime] = None
    exam_score: float
    passed: bool = True
    certificate_qr_url: Optional[str] = None
    skill_delta: Optional[SkillDeltaDto] = None

class TrainingAssignmentRequest(BaseModel):
    employee_id: int
    store_id: int
    trigger_reason: str
    course_code: str
    course_name: str
    deadline_days: int = 5
    is_mandatory: bool = True
    baseline_kpi_value: float = 0.0
    target_kpi_value: float = 0.0
    financial_impact_try: float = 0.0

class EmployeeCompetencyOut(BaseModel):
    id: int
    competency_code: str
    competency_name: str
    score: float
    operational_level: str
    last_evaluated_at: datetime

    class Config:
        from_attributes = True

class EmployeeSkillMatrixItem(BaseModel):
    employee_id: int
    employee_code: str
    full_name: str
    store_id: int
    store_name: str
    department: str
    job_title: str
    is_active: bool
    competencies: List[EmployeeCompetencyOut] = []
    active_training_count: int = 0
    certified_count: int = 0

class TrainingImpactResponse(BaseModel):
    training_id: int
    event_id: str
    employee_name: str
    job_title: str
    store_name: str
    course_name: str
    status: str
    trigger_reason: str
    baseline_kpi_value: float
    target_kpi_value: float
    post_training_kpi_value: Optional[float] = None
    kpi_improvement_pct: float = 0.0
    financial_impact_try: float = 0.0
    financial_saved_try: float = 0.0
    is_goal_achieved: bool = False

# --- Trigger Engine Audit Schemas ---

class TriggerAuditRunResponse(BaseModel):
    audit_timestamp: datetime
    anomalies_detected_count: int
    action_cards_created_count: int
    crm_events_dispatched_count: int
    training_assignments_created_count: int
    summary_messages: List[str] = []

