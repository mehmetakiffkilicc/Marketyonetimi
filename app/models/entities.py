from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.core.database import Base

class StoreType(str, enum.Enum):
    CENTRAL_WAREHOUSE = "CENTRAL_WAREHOUSE"
    STORE = "STORE"

class CampaignType(str, enum.Enum):
    PERCENT_DISCOUNT = "PERCENT_DISCOUNT"      # % İndirim
    BUY_X_PAY_Y = "BUY_X_PAY_Y"                # 3 Al 2 Öde
    SECOND_DISCOUNT = "SECOND_DISCOUNT"        # 2. Ürüne %50
    BASKET_DISCOUNT = "BASKET_DISCOUNT"        # Sepette İndirim

class CampaignStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SENT = "SENT"
    PARTIAL_RECEIVED = "PARTIAL_RECEIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class UserRole(str, enum.Enum):
    PATRON = "PATRON"
    GENEL_MUDUR = "GENEL_MUDUR"
    MAGAZA_MUDURU = "MAGAZA_MUDURU"
    SATIN_ALMACI = "SATIN_ALMACI"
    FINANS_UZMANI = "FINANS_UZMANI"
    DEPO_SORUMLUSU = "DEPO_SORUMLUSU"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True) # Parola hash'i
    role = Column(String(50), default=UserRole.SATIN_ALMACI.value)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False) # E-posta doğrulandı mı?
    verification_token = Column(String(100), nullable=True, index=True) # Doğrulama anahtarı
    category_focus = Column(String(200), nullable=True) # Örn: "Temel Gıda, Şarküteri"
    monthly_budget_limit = Column(Float, default=500000.0) # Aylık stok bağlama bütçe limiti (TL)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="buyer")
    purchase_orders = relationship("PurchaseOrder", back_populates="buyer")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    code = Column(String(50), unique=True, index=True)
    payment_term_days = Column(Integer, default=45) # Ödeme vadesi (gün)
    lead_time_days = Column(Integer, default=3)      # Sipariş teslim süresi (gün)
    target_days_of_inventory = Column(Integer, default=21) # Hedef Yeter Gün Sayısı (gün)
    contact_name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    min_order_amount = Column(Float, default=5000.0) # Minimum sipariş tutarı (TL)

    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    target_margin_pct = Column(Float, default=25.0)     # Hedef Kâr Marjı %
    target_turnover_days = Column(Integer, default=21)  # Hedef Stok Devir Süresi (gün)

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False, index=True)
    brand = Column(String(100), index=True, nullable=True) # Marka (Örn: Bingo, Papia, Familia, Molfix, Fairy, Ariel)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    unit = Column(String(20), default="Adet")          # Adet, KG, Koli, Paket
    purchase_price = Column(Float, nullable=False)     # Alış Fiyatı (KDV Hariç)
    sale_price = Column(Float, nullable=False)         # Satış Fiyatı (KDV Dahil)
    vat_rate = Column(Float, default=0.10)             # KDV Oranı (0.01, 0.10, 0.20)
    shelf_life_days = Column(Integer, default=180)     # Raf Ömrü (gün)
    safety_stock_days = Column(Integer, default=7)     # Emniyet Stoğu (gün)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    buyer = relationship("User", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")
    sales_records = relationship("SalesHistory", back_populates="product")
    campaign_products = relationship("CampaignProduct", back_populates="product")
    po_items = relationship("PurchaseOrderItem", back_populates="product")

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True)
    type = Column(String(50), default=StoreType.STORE.value) # CENTRAL_WAREHOUSE veya STORE
    city = Column(String(50), default="İstanbul")
    district = Column(String(50), nullable=True)
    sqm_area = Column(Float, default=250.0) # Metrekare

    inventory_items = relationship("Inventory", back_populates="store")
    sales_records = relationship("SalesHistory", back_populates="store")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    quantity_on_hand = Column(Float, default=0.0)    # Rafta / Depoda fiziki stok
    quantity_reserved = Column(Float, default=0.0)   # Rezerve stok
    quantity_on_order = Column(Float, default=0.0)    # Tedarikçiden yoldaki sipariş
    last_counted_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_items")
    store = relationship("Store", back_populates="inventory_items")

class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sale_date = Column(Date, nullable=False, index=True)
    quantity_sold = Column(Float, default=0.0)
    gross_revenue = Column(Float, default=0.0) # Brüt Satış Tutarı (TL)
    cogs = Column(Float, default=0.0)          # Satılan Malın Maliyeti (TL)
    was_on_campaign = Column(Boolean, default=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    product = relationship("Product", back_populates="sales_records")
    store = relationship("Store", back_populates="sales_records")
    campaign = relationship("Campaign", back_populates="sales_records")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    campaign_type = Column(String(50), default=CampaignType.PERCENT_DISCOUNT.value)
    discount_rate = Column(Float, default=0.15) # %15 indirim
    application_channel = Column(String(50), default="DİREKT_RAF") # DİREKT_RAF, DİJİTAL_KART, HER_İKİSİ
    status = Column(String(50), default=CampaignStatus.PLANNED.value)
    
    target_sales_qty = Column(Float, default=0.0)
    target_revenue = Column(Float, default=0.0)
    actual_sales_qty = Column(Float, default=0.0)
    actual_revenue = Column(Float, default=0.0)
    created_from_po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    notes = Column(Text, nullable=True)

    campaign_products = relationship("CampaignProduct", back_populates="campaign", cascade="all, delete-orphan")
    sales_records = relationship("SalesHistory", back_populates="campaign")
    created_from_po = relationship("PurchaseOrder", back_populates="linked_campaigns")

class CampaignProduct(Base):
    __tablename__ = "campaign_products"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    regular_shelf_price = Column(Float, nullable=True) # Normal Raf Satış Fiyatı (TL)
    promotional_price = Column(Float, nullable=True)   # Aktivite / Kampanya Satış Fiyatı (TL)
    discount_rate = Column(Float, default=0.15)
    target_sales_qty = Column(Float, default=0.0)      # Bu ürün için hedeflenen aktivite satış adedi
    application_channel = Column(String(50), default="DİREKT_RAF") # DİREKT_RAF, DİJİTAL_KART, HER_İKİSİ

    campaign = relationship("Campaign", back_populates="campaign_products")
    product = relationship("Product", back_populates="campaign_products")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(Date, default=date.today)
    expected_delivery_date = Column(Date, nullable=True)
    status = Column(String(50), default=POStatus.DRAFT.value)
    total_cost = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    buyer = relationship("User", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    linked_campaigns = relationship("Campaign", back_populates="created_from_po")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    suggested_quantity = Column(Float, default=0.0) # AI / Algoritma önerisi
    ordered_quantity = Column(Float, default=0.0)   # Kesinleşen sipariş
    unit_cost = Column(Float, nullable=False)
    planned_campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="po_items")

class ActionCardStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"

class ActionCardPriority(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ActionCard(Base):
    __tablename__ = "action_cards"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(50), unique=True, index=True, nullable=False)
    source_module = Column(String(50), nullable=False) # SALES_LOSS, STOCKOUT, FRESH_WASTE, AUDIT_FAIL, EXCESS_STOCK
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    financial_impact_try = Column(Float, default=0.0)
    actual_recovered_try = Column(Float, default=0.0)
    assigned_to = Column(String(100), nullable=True)
    approver = Column(String(100), nullable=True)
    priority = Column(String(20), default=ActionCardPriority.MEDIUM.value)
    status = Column(String(20), default=ActionCardStatus.OPEN.value)
    deadline_date = Column(Date, nullable=True)
    resolution_evidence = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    department = Column(String(50), default="RETAIL_OPERATIONS") # MEAT_AND_BUTCHERY, BAKERY, CASH_DESK, FRUIT_VEG
    job_title = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store")
    competencies = relationship("EmployeeCompetency", back_populates="employee", cascade="all, delete-orphan")
    training_assignments = relationship("TrainingAssignment", back_populates="employee", cascade="all, delete-orphan")
    certifications = relationship("CertificationLog", back_populates="employee", cascade="all, delete-orphan")

class EmployeeCompetency(Base):
    __tablename__ = "employee_competencies"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    competency_code = Column(String(50), nullable=False) # MEAT_YIELD_MANAGEMENT, HYGIENE_HACCP, CASHIER_SPEED
    competency_name = Column(String(150), nullable=False)
    score = Column(Float, default=50.0) # 0 - 100
    operational_level = Column(String(50), default="INTERMEDIATE") # NOVICE, INTERMEDIATE, SENIOR_BUTCHER, MASTER
    last_evaluated_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="competencies")

class TrainingAssignment(Base):
    __tablename__ = "training_assignments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    trigger_reason = Column(String(100), nullable=False) # CARCASS_YIELD_DEFICIT, HIGH_WASTE_ANOMALY, HYGIENE_AUDIT_FAIL
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(200), nullable=False)
    deadline_days = Column(Integer, default=5)
    is_mandatory = Column(Boolean, default=True)
    status = Column(String(30), default="ASSIGNED") # ASSIGNED, IN_PROGRESS, COMPLETED, OVERDUE
    baseline_kpi_value = Column(Float, default=0.0)
    target_kpi_value = Column(Float, default=0.0)
    post_training_kpi_value = Column(Float, nullable=True)
    financial_impact_try = Column(Float, default=0.0)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="training_assignments")
    store = relationship("Store")

class CertificationLog(Base):
    __tablename__ = "certification_logs"

    id = Column(Integer, primary_key=True, index=True)
    certificate_event_id = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(200), nullable=False)
    exam_score = Column(Float, nullable=False)
    passed = Column(Boolean, default=True)
    certificate_qr_url = Column(Text, nullable=True)
    issued_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="certifications")

class CRMEventLog(Base):
    __tablename__ = "crm_event_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    event_type = Column(String(50), nullable=False) # INVENTORY_OVERSTOCK_ALERT, CATEGORY_CHURN_DETECTED
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    payload_json = Column(Text, nullable=False)
    status = Column(String(30), default="DISPATCHED") # DISPATCHED, PROCESSED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store")
    product = relationship("Product")

class CRMCampaignFeedback(Base):
    __tablename__ = "crm_campaign_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(100), index=True, nullable=False)
    origin_event_id = Column(String(50), nullable=True)
    targeted_customers = Column(Integer, default=0)
    messages_delivered = Column(Integer, default=0)
    coupons_redeemed = Column(Integer, default=0)
    conversion_rate_pct = Column(Float, default=0.0)
    total_revenue_generated_try = Column(Float, default=0.0)
    units_sold = Column(Integer, default=0)
    remaining_excess_units = Column(Integer, default=0)
    incremental_basket_revenue_try = Column(Float, default=0.0)
    dominant_segment = Column(String(100), nullable=True)
    avg_total_basket_value_try = Column(Float, default=0.0)
    churn_prevented_customer_count = Column(Integer, default=0)
    received_at = Column(DateTime, default=datetime.utcnow)

class TriggerEventLog(Base):
    __tablename__ = "trigger_event_logs"

    id = Column(Integer, primary_key=True, index=True)
    trigger_type = Column(String(50), nullable=False)
    source_module = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    target_system = Column(String(50), nullable=False) # XPLUS_CRM, PERAKENDE_AKADEMI, ACTION_CARD_ENGINE
    status = Column(String(30), default="SUCCESS")
    created_at = Column(DateTime, default=datetime.utcnow)

