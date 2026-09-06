from datetime import date, timedelta
import random
from sqlalchemy.orm import Session
from app.models.entities import (
    User, Supplier, Category, Product, Store, Inventory,
    SalesHistory, Campaign, CampaignProduct, PurchaseOrder, PurchaseOrderItem,
    StoreType, CampaignType, CampaignStatus, POStatus,
    Employee, EmployeeCompetency, TrainingAssignment, CertificationLog,
    CRMEventLog, CRMCampaignFeedback, TriggerEventLog, ActionCard,
    ActionCardStatus, ActionCardPriority
)
from datetime import datetime

def seed_database(db: Session):
    # Temiz tohumlama için mevcut verileri temizle
    db.query(ActionCard).delete()
    db.query(EmployeeCompetency).delete()
    db.query(TrainingAssignment).delete()
    db.query(CertificationLog).delete()
    db.query(CRMEventLog).delete()
    db.query(CRMCampaignFeedback).delete()
    db.query(TriggerEventLog).delete()
    db.query(Employee).delete()
    db.query(SalesHistory).delete()
    db.query(CampaignProduct).delete()
    db.query(Campaign).delete()
    db.query(PurchaseOrderItem).delete()
    db.query(PurchaseOrder).delete()
    db.query(Inventory).delete()
    db.query(Product).delete()
    db.query(Store).delete()
    db.query(Category).delete()
    db.query(Supplier).delete()
    db.query(User).delete()
    db.flush()

    print("Veritabanı zengin tohumlama (seeding) başlatılıyor...")

    # 1. Kullanıcılar & Satın Almacılar
    buyers = [
        User(name="Ahmet Kılıç", email="ahmet.k@smartretail.com", role="SATIN_ALMACI", category_focus="Süt & Kahvaltılık, Temel Gıda", monthly_budget_limit=1500000.0),
        User(name="Zeynep Turan", email="zeynep.t@smartretail.com", role="SATIN_ALMACI", category_focus="Ev Bakım & Temizlik, Kişisel Bakım", monthly_budget_limit=1200000.0),
        User(name="Mehmet Saygın", email="mehmet.s@smartretail.com", role="SATIN_ALMACI", category_focus="Atıştırmalık, İçecek", monthly_budget_limit=1000000.0),
        User(name="Patron Selim", email="patron@smartretail.com", role="PATRON", category_focus="Tümü", monthly_budget_limit=5000000.0),
    ]
    db.add_all(buyers)
    db.flush()

    # 2. Tedarikçiler / Üreticiler
    suppliers = [
        Supplier(name="Eti Gıda San. A.Ş.", code="SUP_ETI", payment_term_days=45, lead_time_days=3, contact_name="Kemal Eti", phone="0212 555 1003", min_order_amount=15000.0),
        Supplier(name="Sütaş Süt Ürünleri A.Ş.", code="SUP_SUTAS", payment_term_days=30, lead_time_days=2, contact_name="Ali Sütaş", phone="0212 555 1001", min_order_amount=25000.0),
        Supplier(name="Unilever Türkiye", code="SUP_UNILEVER", payment_term_days=60, lead_time_days=4, contact_name="Deniz Ak", phone="0212 555 1002", min_order_amount=40000.0),
        Supplier(name="Procter & Gamble (P&G)", code="SUP_PG", payment_term_days=75, lead_time_days=5, contact_name="Seda Gül", phone="0212 555 1004", min_order_amount=50000.0),
        Supplier(name="Hayat Kimya A.Ş.", code="SUP_HAYAT", payment_term_days=45, lead_time_days=3, contact_name="Murat Hayat", phone="0212 555 1005", min_order_amount=30000.0),
        Supplier(name="Ülker Bisküvi (Pladis)", code="SUP_ULKER", payment_term_days=45, lead_time_days=2, contact_name="Can Ülker", phone="0212 555 1006", min_order_amount=20000.0),
        Supplier(name="Coca-Cola İçecek A.Ş.", code="SUP_COCACOLA", payment_term_days=30, lead_time_days=2, contact_name="Banu Kola", phone="0212 555 1007", min_order_amount=25000.0),
        Supplier(name="Tat Gıda Sanayi A.Ş.", code="SUP_TAT", payment_term_days=45, lead_time_days=3, contact_name="Hakan Tat", phone="0212 555 1008", min_order_amount=20000.0),
    ]
    db.add_all(suppliers)
    db.flush()

    # 3. Kategoriler
    categories = [
        Category(name="Atıştırmalık & Bisküvi", code="CAT_ATISTIR", target_margin_pct=28.0, target_turnover_days=20),
        Category(name="Süt & Kahvaltılık", code="CAT_SUT", target_margin_pct=22.0, target_turnover_days=14),
        Category(name="Temel Gıda & Konserve", code="CAT_TEMEL", target_margin_pct=18.0, target_turnover_days=25),
        Category(name="İçecek", code="CAT_ICECEK", target_margin_pct=25.0, target_turnover_days=15),
        Category(name="Ev Bakım & Temizlik", code="CAT_TEMIZLIK", target_margin_pct=30.0, target_turnover_days=35),
        Category(name="Kişisel Bakım", code="CAT_BAKIM", target_margin_pct=35.0, target_turnover_days=40),
    ]
    db.add_all(categories)
    db.flush()

    # 4. Şubeler ve Depolar
    stores = [
        Store(name="Samandıra Merkez Depo", code="DEP_SAMANDIRA", type=StoreType.CENTRAL_WAREHOUSE.value, city="İstanbul", district="Sancaktepe", sqm_area=2500.0),
        Store(name="Kadıköy Şube", code="MAG_KADIKOY", type=StoreType.STORE.value, city="İstanbul", district="Kadıköy", sqm_area=350.0),
        Store(name="Beşiktaş Şube", code="MAG_BESIKTAS", type=StoreType.STORE.value, city="İstanbul", district="Beşiktaş", sqm_area=300.0),
        Store(name="Üsküdar Şube", code="MAG_USKUDAR", type=StoreType.STORE.value, city="İstanbul", district="Üsküdar", sqm_area=400.0),
        Store(name="Bakırköy Şube", code="MAG_BAKIRKOY", type=StoreType.STORE.value, city="İstanbul", district="Bakırköy", sqm_area=450.0),
        Store(name="Şişli Şube", code="MAG_SISLI", type=StoreType.STORE.value, city="İstanbul", district="Şişli", sqm_area=320.0),
    ]
    db.add_all(stores)
    db.flush()

    # Map helpers
    cat_map = {c.name: c.id for c in categories}
    sup_map = {s.name: s.id for s in suppliers}
    buyer_ahmet = buyers[0].id
    buyer_zeynep = buyers[1].id
    buyer_mehmet = buyers[2].id

    # 5. Ürünler (Barkod, Ürün Adı, Marka, Kategori, Tedarikçi, Satın Almacı, Birim, Alış, Satış, KDV, Raf Ömrü, Emniyet Günü)
    raw_products = [
        # Eti (Mehmet)
        ("8690555024", "Eti Negro / Nero Bisküvi 110 Gr", "Eti", "Atıştırmalık & Bisküvi", "Eti Gıda San. A.Ş.", buyer_mehmet, "Adet", 11.50, 17.50, 0.10, 360, 7),
        ("8690555025", "Eti Karam Gurme Bitter Çikolata 50 Gr", "Eti", "Atıştırmalık & Bisküvi", "Eti Gıda San. A.Ş.", buyer_mehmet, "Adet", 12.00, 18.00, 0.10, 240, 7),
        ("8690555026", "Eti Crax Çubuk Kraker Baharatlı 50 Gr", "Eti", "Atıştırmalık & Bisküvi", "Eti Gıda San. A.Ş.", buyer_mehmet, "Adet", 6.50, 10.00, 0.10, 360, 5),
        ("8690555027", "Eti Burçak Bisküvi 3'lü Paket", "Eti", "Atıştırmalık & Bisküvi", "Eti Gıda San. A.Ş.", buyer_mehmet, "Adet", 28.00, 42.50, 0.10, 360, 8),
        ("8690555028", "Eti Lifalif Yulaf Ezmesi 500 Gr", "Eti", "Atıştırmalık & Bisküvi", "Eti Gıda San. A.Ş.", buyer_mehmet, "Adet", 35.00, 52.50, 0.10, 360, 10),

        # Sütaş (Ahmet)
        ("8690555001", "Sütaş Tam Yağlı Süt 1 LT", "Sütaş", "Süt & Kahvaltılık", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, "Adet", 28.50, 39.50, 0.01, 90, 7),
        ("8690555002", "Sütaş Doğal Yoğurt 1500 Gr", "Sütaş", "Süt & Kahvaltılık", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, "Adet", 58.00, 79.90, 0.01, 30, 5),
        ("8690555003", "Sütaş Kaşar Peyniri 600 Gr", "Sütaş", "Süt & Kahvaltılık", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, "Adet", 175.00, 245.00, 0.01, 120, 10),
        ("8690555004", "Sütaş Süzme Peynir 500 Gr", "Sütaş", "Süt & Kahvaltılık", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, "Adet", 72.00, 99.50, 0.01, 90, 7),
        ("8690555005", "Sütaş Ayran 1 LT", "Sütaş", "Süt & Kahvaltılık", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, "Adet", 22.00, 32.50, 0.01, 20, 4),
        
        # Tat Gıda (Ahmet)
        ("8690555006", "Tat Domates Salçası 830 Gr", "Tat", "Temel Gıda & Konserve", "Tat Gıda Sanayi A.Ş.", buyer_ahmet, "Adet", 42.00, 59.90, 0.01, 720, 14),
        ("8690555007", "Tat Ketçap Tatlı 650 Gr", "Tat", "Temel Gıda & Konserve", "Tat Gıda Sanayi A.Ş.", buyer_ahmet, "Adet", 34.00, 48.50, 0.01, 360, 10),
        ("8690555008", "Tat Bezelye Konservesi 680 Gr", "Tat", "Temel Gıda & Konserve", "Tat Gıda Sanayi A.Ş.", buyer_ahmet, "Adet", 26.50, 37.90, 0.01, 720, 14),
        ("8690555009", "Tat Garnitür 560 Gr", "Tat", "Temel Gıda & Konserve", "Tat Gıda Sanayi A.Ş.", buyer_ahmet, "Adet", 24.00, 34.50, 0.01, 720, 14),

        # Unilever (Zeynep)
        ("8690555010", "Domestos Çamaşır Suyu 750 ML", "Domestos", "Ev Bakım & Temizlik", "Unilever Türkiye", buyer_zeynep, "Adet", 32.00, 49.90, 0.20, 720, 10),
        ("8690555011", "Cif Krem Yüzey Temizleyici 750 ML", "Cif", "Ev Bakım & Temizlik", "Unilever Türkiye", buyer_zeynep, "Adet", 38.00, 57.50, 0.20, 720, 10),
        ("8690555012", "Omo Sıvı Çamaşır Deterjanı 1690 ML", "Omo", "Ev Bakım & Temizlik", "Unilever Türkiye", buyer_zeynep, "Adet", 155.00, 229.90, 0.20, 720, 14),
        ("8690555013", "Dove Nemlendirici Sıvı Sabun 500 ML", "Dove", "Kişisel Bakım", "Unilever Türkiye", buyer_zeynep, "Adet", 48.00, 74.90, 0.20, 720, 12),
        ("8690555014", "Clear Şampuan Kepeğe Karşı 600 ML", "Clear", "Kişisel Bakım", "Unilever Türkiye", buyer_zeynep, "Adet", 85.00, 129.90, 0.20, 720, 14),

        # P&G (Zeynep)
        ("8690555015", "Ariel Dağ Esintisi Toz Deterjan 6 KG", "Ariel", "Ev Bakım & Temizlik", "Procter & Gamble (P&G)", buyer_zeynep, "Adet", 280.00, 399.90, 0.20, 720, 14),
        ("8690555016", "Fairy Bulaşık Sıvısı Limon 1350 ML", "Fairy", "Ev Bakım & Temizlik", "Procter & Gamble (P&G)", buyer_zeynep, "Adet", 68.00, 99.90, 0.20, 720, 10),
        ("8690555017", "Fairy Platinum Bulaşık Tableti 60'lı", "Fairy", "Ev Bakım & Temizlik", "Procter & Gamble (P&G)", buyer_zeynep, "Adet", 295.00, 429.00, 0.20, 720, 15),
        ("8690555018", "Head & Shoulders Şampuan 400 ML", "Head & Shoulders", "Kişisel Bakım", "Procter & Gamble (P&G)", buyer_zeynep, "Adet", 92.00, 139.90, 0.20, 720, 12),
        ("8690555019", "Prima Bebek Bezi Fırsat Paketi No:4", "Prima", "Kişisel Bakım", "Procter & Gamble (P&G)", buyer_zeynep, "Adet", 340.00, 479.90, 0.20, 1080, 15),

        # Hayat Kimya (Zeynep) - Markalar: Bingo, Papia, Familia, Molfix, Molped
        ("8690555020", "Bingo Sıvı Bakım Deterjanı 3 LT", "Bingo", "Ev Bakım & Temizlik", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 110.00, 159.90, 0.20, 720, 12),
        ("8690555041", "Bingo Oksijen Hijyen Çamaşır Suyu 750 ML", "Bingo", "Ev Bakım & Temizlik", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 34.00, 52.50, 0.20, 720, 10),
        ("8690555021", "Papia Tuvalet Kağıdı 32'li", "Papia", "Ev Bakım & Temizlik", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 195.00, 289.90, 0.20, 1080, 14),
        ("8690555042", "Papia İpek Özlü Kağıt Peçete 100'lü", "Papia", "Ev Bakım & Temizlik", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 28.00, 42.00, 0.20, 1080, 10),
        ("8690555022", "Familia Havlu Kağıt 12'li", "Familia", "Ev Bakım & Temizlik", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 115.00, 169.90, 0.20, 1080, 14),
        ("8690555043", "Familia Plus Tuvalet Kağıdı 16'lı", "Familia", "Ev Bakım & Temizlik", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 110.00, 165.00, 0.20, 1080, 12),
        ("8690555023", "Molfix Maxi Bebek Bezi 74'lü", "Molfix", "Kişisel Bakım", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 260.00, 369.90, 0.20, 1080, 14),
        ("8690555040", "Molped Gece Hijyenik Ped 14'lü", "Molped", "Kişisel Bakım", "Hayat Kimya A.Ş.", buyer_zeynep, "Adet", 45.00, 68.90, 0.20, 1080, 10),

        # Ülker (Mehmet)
        ("8690555029", "Ülker Çikolatalı Gofret 36 Gr", "Ülker", "Atıştırmalık & Bisküvi", "Ülker Bisküvi (Pladis)", buyer_mehmet, "Adet", 8.00, 12.50, 0.10, 360, 5),
        ("8690555030", "Ülker Pötibör Bisküvi 800 Gr", "Ülker", "Atıştırmalık & Bisküvi", "Ülker Bisküvi (Pladis)", buyer_mehmet, "Adet", 38.00, 55.00, 0.10, 360, 10),
        ("8690555031", "Ülker Çizi Kraker 4'lü Paket", "Ülker", "Atıştırmalık & Bisküvi", "Ülker Bisküvi (Pladis)", buyer_mehmet, "Adet", 22.00, 32.50, 0.10, 360, 7),
        ("8690555032", "Ülker Çokokrem Kakaolu Fındık Kreması 650 Gr", "Çokokrem", "Süt & Kahvaltılık", "Ülker Bisküvi (Pladis)", buyer_mehmet, "Adet", 78.00, 115.00, 0.10, 360, 10),
        ("8690555033", "Ülker Halley Bisküvi 10'lu Paket", "Halley", "Atıştırmalık & Bisküvi", "Ülker Bisküvi (Pladis)", buyer_mehmet, "Adet", 32.00, 48.00, 0.10, 360, 8),

        # Coca-Cola (Mehmet)
        ("8690555034", "Coca-Cola Orijinal Tat 1 LT Pet", "Coca-Cola", "İçecek", "Coca-Cola İçecek A.Ş.", buyer_mehmet, "Adet", 24.00, 35.00, 0.10, 180, 5),
        ("8690555035", "Coca-Cola Zero Sugar 1 LT Pet", "Coca-Cola", "İçecek", "Coca-Cola İçecek A.Ş.", buyer_mehmet, "Adet", 24.00, 35.00, 0.10, 180, 5),
        ("8690555036", "Fanta Portakal 1 LT Pet", "Fanta", "İçecek", "Coca-Cola İçecek A.Ş.", buyer_mehmet, "Adet", 23.00, 33.50, 0.10, 180, 5),
        ("8690555037", "Sprite Gazoz 1 LT Pet", "Sprite", "İçecek", "Coca-Cola İçecek A.Ş.", buyer_mehmet, "Adet", 23.00, 33.50, 0.10, 180, 5),
        ("8690555038", "Fuse Tea Şeftali Soğuk Çay 1 LT", "Fuse Tea", "İçecek", "Coca-Cola İçecek A.Ş.", buyer_mehmet, "Adet", 22.00, 32.00, 0.10, 240, 5),
        ("8690555039", "Cappy %100 Karışık Meyve Suyu 1 LT", "Cappy", "İçecek", "Coca-Cola İçecek A.Ş.", buyer_mehmet, "Adet", 29.00, 42.50, 0.10, 360, 7),
    ]

    product_objects = []
    prod_by_code = {}
    for barcode, name, brand, cat_name, sup_name, buyer_id, unit, p_price, s_price, vat, shelf_life, safety_days in raw_products:
        p = Product(
            barcode=barcode,
            name=name,
            brand=brand,
            category_id=cat_map[cat_name],
            supplier_id=sup_map[sup_name],
            buyer_id=buyer_id,
            unit=unit,
            purchase_price=p_price,
            sale_price=s_price,
            vat_rate=vat,
            shelf_life_days=shelf_life,
            safety_stock_days=safety_days
        )
        db.add(p)
        product_objects.append(p)
        prod_by_code[barcode] = p
    
    db.flush()

    # 6. Geçmiş Aktivite & Kampanyalar (Haziran, Temmuz, Ağustos 2026)
    # Eti Aktiviteleri
    camp_eti_1 = Campaign(
        title="12 - 20 Haziran Eti Bisküvi Haftası",
        start_date=date(2026, 6, 12),
        end_date=date(2026, 6, 20),
        campaign_type=CampaignType.PERCENT_DISCOUNT.value,
        discount_rate=0.15,
        status=CampaignStatus.COMPLETED.value,
        target_sales_qty=3200.0,
        target_revenue=48000.0,
        actual_sales_qty=3410.0,
        actual_revenue=51150.0,
        notes="Eti Negro ve Burçak için %15 indirim aktivitesi."
    )
    camp_eti_2 = Campaign(
        title="15 - 24 Temmuz Eti Çikolata & Gurme Günleri",
        start_date=date(2026, 7, 15),
        end_date=date(2026, 7, 24),
        campaign_type=CampaignType.PERCENT_DISCOUNT.value,
        discount_rate=0.20,
        status=CampaignStatus.COMPLETED.value,
        target_sales_qty=2200.0,
        target_revenue=33000.0,
        actual_sales_qty=2380.0,
        actual_revenue=35700.0,
        notes="Karam Gurme ve Crax aktivitesi."
    )
    camp_eti_3 = Campaign(
        title="10 - 20 Ağustos Çıtır Çıtır Kraker Festivali",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 20),
        campaign_type=CampaignType.PERCENT_DISCOUNT.value,
        discount_rate=0.15,
        status=CampaignStatus.COMPLETED.value,
        target_sales_qty=2800.0,
        target_revenue=25000.0,
        actual_sales_qty=2950.0,
        actual_revenue=26550.0,
        notes="Eti Crax ve Lifalif aktivitesi."
    )

    # Sütaş Aktiviteleri
    camp_sutas_1 = Campaign(
        title="10 - 18 Temmuz Sütaş Süt ve Yoğurt Yaz Kampanyası",
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 18),
        campaign_type=CampaignType.PERCENT_DISCOUNT.value,
        discount_rate=0.15,
        status=CampaignStatus.COMPLETED.value,
        target_sales_qty=4500.0,
        target_revenue=180000.0,
        actual_sales_qty=4820.0,
        actual_revenue=192800.0,
        notes="Sütaş Süt ve Yoğurt şenliği."
    )
    camp_sutas_2 = Campaign(
        title="5 - 15 Ağustos Sütaş Peynir Şöleni",
        start_date=date(2026, 8, 5),
        end_date=date(2026, 8, 15),
        campaign_type=CampaignType.PERCENT_DISCOUNT.value,
        discount_rate=0.18,
        status=CampaignStatus.COMPLETED.value,
        target_sales_qty=1200.0,
        target_revenue=240000.0,
        actual_sales_qty=1350.0,
        actual_revenue=270000.0,
        notes="Sütaş Kaşar ve Süzme peynir aktivitesi."
    )

    # P&G Aktivitesi
    camp_pg_1 = Campaign(
        title="1 - 10 Ağustos P&G Temizlik Festivali",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 10),
        campaign_type=CampaignType.PERCENT_DISCOUNT.value,
        discount_rate=0.20,
        status=CampaignStatus.COMPLETED.value,
        target_sales_qty=1800.0,
        target_revenue=350000.0,
        actual_sales_qty=1650.0,
        actual_revenue=322000.0,
        notes="Ariel ve Fairy Platinum aktivitesi."
    )

    all_campaigns = [camp_eti_1, camp_eti_2, camp_eti_3, camp_sutas_1, camp_sutas_2, camp_pg_1]
    db.add_all(all_campaigns)
    db.flush()

    # Kampanya Ürün Eşleştirmeleri
    # Eti
    db.add(CampaignProduct(campaign_id=camp_eti_1.id, product_id=prod_by_code["8690555024"].id, promotional_price=14.90))
    db.add(CampaignProduct(campaign_id=camp_eti_1.id, product_id=prod_by_code["8690555027"].id, promotional_price=36.00))
    db.add(CampaignProduct(campaign_id=camp_eti_2.id, product_id=prod_by_code["8690555025"].id, promotional_price=14.50))
    db.add(CampaignProduct(campaign_id=camp_eti_2.id, product_id=prod_by_code["8690555026"].id, promotional_price=8.00))
    db.add(CampaignProduct(campaign_id=camp_eti_3.id, product_id=prod_by_code["8690555026"].id, promotional_price=8.50))
    db.add(CampaignProduct(campaign_id=camp_eti_3.id, product_id=prod_by_code["8690555028"].id, promotional_price=44.50))

    # Sütaş
    db.add(CampaignProduct(campaign_id=camp_sutas_1.id, product_id=prod_by_code["8690555001"].id, promotional_price=33.50))
    db.add(CampaignProduct(campaign_id=camp_sutas_1.id, product_id=prod_by_code["8690555002"].id, promotional_price=67.90))
    db.add(CampaignProduct(campaign_id=camp_sutas_2.id, product_id=prod_by_code["8690555003"].id, promotional_price=205.00))
    db.add(CampaignProduct(campaign_id=camp_sutas_2.id, product_id=prod_by_code["8690555004"].id, promotional_price=82.50))

    # P&G
    db.add(CampaignProduct(campaign_id=camp_pg_1.id, product_id=prod_by_code["8690555015"].id, promotional_price=319.90))
    db.add(CampaignProduct(campaign_id=camp_pg_1.id, product_id=prod_by_code["8690555017"].id, promotional_price=349.00))

    db.flush()

    # 7. Stok ve 90 Günlük Satış Geçmişi Simülasyonu
    today = date(2026, 9, 1)
    central_depot = [s for s in stores if s.type == StoreType.CENTRAL_WAREHOUSE.value][0]
    sub_stores = [s for s in stores if s.type == StoreType.STORE.value]

    random.seed(42)

    # Product to active campaign mapper
    # product_id -> list of (start_date, end_date, campaign_id, discount_rate)
    prod_camp_map = {}
    for camp in all_campaigns:
        cps = db.query(CampaignProduct).filter(CampaignProduct.campaign_id == camp.id).all()
        for cp in cps:
            if cp.product_id not in prod_camp_map:
                prod_camp_map[cp.product_id] = []
            prod_camp_map[cp.product_id].append((camp.start_date, camp.end_date, camp.id, camp.discount_rate))

    # Her ürün için stok seviyeleri oluşturalım
    for p_idx, prod in enumerate(product_objects):
        base_daily_store_rate = random.uniform(8.0, 22.0)

        # Depo Stoğu ve Şube Stokları:
        if p_idx in [5, 14, 19]: # Sütaş Süt, Domestos, Ariel -> Depoda BOL var ama 2 şubede 0 (İkmal uyuşmazlığı)
            central_qty = random.uniform(800, 1500)
            db.add(Inventory(product_id=prod.id, store_id=central_depot.id, quantity_on_hand=central_qty, quantity_on_order=0))
            for s_idx, st in enumerate(sub_stores):
                st_qty = 0.0 if s_idx in [0, 1] else random.uniform(15.0, 40.0)
                db.add(Inventory(product_id=prod.id, store_id=st.id, quantity_on_hand=st_qty, quantity_on_order=0))
        elif p_idx in [23, 24]: # Bingo, Papia -> Overstock
            central_qty = random.uniform(2500, 4000)
            db.add(Inventory(product_id=prod.id, store_id=central_depot.id, quantity_on_hand=central_qty, quantity_on_order=0))
            for st in sub_stores:
                st_qty = random.uniform(80.0, 150.0)
                db.add(Inventory(product_id=prod.id, store_id=st.id, quantity_on_hand=st_qty, quantity_on_order=0))
        else: # Normal
            central_qty = random.uniform(150, 400)
            db.add(Inventory(product_id=prod.id, store_id=central_depot.id, quantity_on_hand=central_qty, quantity_on_order=random.choice([0, 100, 200])))
            for st in sub_stores:
                st_qty = random.uniform(15.0, 60.0)
                db.add(Inventory(product_id=prod.id, store_id=st.id, quantity_on_hand=st_qty, quantity_on_order=0))

        # Son 90 günün satış kayıtlarını oluşturalım (2026-06-03 ile 2026-08-31 arası)
        camps_for_prod = prod_camp_map.get(prod.id, [])

        for days_back in range(90, 0, -1):
            cur_date = today - timedelta(days=days_back)
            
            # Kampanya kontrolü
            active_cid = None
            discount_r = 0.0
            for c_start, c_end, c_id, d_rate in camps_for_prod:
                if c_start <= cur_date <= c_end:
                    active_cid = c_id
                    discount_r = d_rate
                    break

            is_camp = bool(active_cid)
            camp_lift = 2.5 if is_camp else 1.0
            weekend_multiplier = 1.35 if cur_date.weekday() in [5, 6] else 1.0

            for st in sub_stores:
                # İkmal uyuşmazlığı simülasyonu
                if p_idx in [5, 14, 19] and st.code in ["MAG_KADIKOY", "MAG_BESIKTAS"] and days_back <= 5:
                    continue

                daily_qty = round(max(0, random.gauss(base_daily_store_rate * weekend_multiplier * camp_lift, 2.0)))
                if daily_qty > 0:
                    unit_sale = prod.sale_price * (1.0 - discount_r)
                    gross_rev = round(daily_qty * unit_sale, 2)
                    cogs_val = round(daily_qty * prod.purchase_price, 2)

                    db.add(SalesHistory(
                        product_id=prod.id,
                        store_id=st.id,
                        sale_date=cur_date,
                        quantity_sold=daily_qty,
                        gross_revenue=gross_rev,
                        cogs=cogs_val,
                        was_on_campaign=is_camp,
                        campaign_id=active_cid
                    ))

    db.flush()

    # 8. Başlangıç Satın Alma Siparişleri (Tarih ve Vade Takip Raporu için)
    po_seeds = [
        # (PO_No, Tedarikçi, Satın Almacı, Sipariş Tarihi, Teslim Tarihi, Durum, Not, [(ÜrünIndex, Adet)])
        ("PO-2026-0710", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, date(2026, 7, 25), date(2026, 7, 27), "COMPLETED", "Temmuz sonu peynir ve tereyağı partisi (Vadesi 6 gün geçti)", [(7, 800), (8, 600)]),
        ("PO-2026-0720", "Ülker Bisküvi (Pladis)", buyer_mehmet, date(2026, 7, 15), date(2026, 7, 18), "COMPLETED", "Temmuz ortası bisküvi ve çikolata ikmali (Vadesi Bugün)", [(2, 2000), (3, 3000)]),
        ("PO-2026-0725", "Eti Gıda San. A.Ş.", buyer_mehmet, date(2026, 7, 20), date(2026, 7, 23), "COMPLETED", "Bisküvi ve atıştırmalık partisi (Vadeye 5 Gün)", [(0, 1200), (1, 900)]),
        ("PO-2026-0808", "Coca-Cola İçecek A.Ş.", buyer_mehmet, date(2026, 8, 10), date(2026, 8, 12), "COMPLETED", "Meşrubat ve soğuk çay ana ikmali (Vadeye 10 Gün)", [(31, 3000), (32, 2000)]),
        ("PO-2026-0802", "Sütaş Süt Ürünleri A.Ş.", buyer_ahmet, date(2026, 8, 18), date(2026, 8, 20), "COMPLETED", "Süt ve kahvaltılık haftalık rutin ikmali (Vadeye 18 Gün)", [(5, 3000), (6, 1500), (7, 500), (8, 800)]),
        ("PO-2026-0801", "Hayat Kimya A.Ş.", buyer_zeynep, date(2026, 8, 10), date(2026, 8, 13), "COMPLETED", "Ağustos başı hijyen ve kağıt ikmali (Vadeye 26 Gün)", [(20, 1500), (22, 1200), (24, 800), (26, 600)]),
        ("PO-2026-0803", "Unilever Türkiye", buyer_zeynep, date(2026, 8, 24), date(2026, 8, 27), "COMPLETED", "Domestos ve Omo çamaşır deterjanı ana parti", [(14, 2000), (16, 1000), (17, 800)]),
        ("PO-2026-0804", "Procter & Gamble (P&G)", buyer_zeynep, date(2026, 8, 28), date(2026, 9, 2), "SENT", "Ariel & Fairy eylül başı büyük kampanya stoğu", [(19, 1200), (20, 2500), (21, 1500)]),
        ("PO-2026-0901", "Eti Gıda San. A.Ş.", buyer_mehmet, date(2026, 9, 1), date(2026, 9, 4), "APPROVED", "Okul açılışı atıştırmalık ve bisküvi siparişi", [(0, 3500), (1, 2000), (3, 2500), (4, 1500)]),
        ("PO-2026-0902", "Hayat Kimya A.Ş.", buyer_zeynep, date(2026, 9, 1), date(2026, 9, 5), "APPROVED", "Papia & Familia kağıt grubu eylül fırsat siparişi", [(22, 2000), (23, 1000), (24, 1500), (25, 800)]),
    ]

    for po_num, sup_name, b_id, o_date, d_date, st_val, po_note, item_tuples in po_seeds:
        sup_id = sup_map[sup_name]
        po_obj = PurchaseOrder(
            po_number=po_num,
            supplier_id=sup_id,
            buyer_id=b_id,
            order_date=o_date,
            expected_delivery_date=d_date,
            status=st_val,
            total_cost=0.0,
            notes=po_note
        )
        db.add(po_obj)
        db.flush()

        po_tot = 0.0
        for p_idx, qty in item_tuples:
            if p_idx < len(product_objects):
                target_prod = product_objects[p_idx]
                cost_val = target_prod.purchase_price
                po_tot += qty * cost_val
                
                db.add(PurchaseOrderItem(
                    po_id=po_obj.id,
                    product_id=target_prod.id,
                    suggested_quantity=qty,
                    ordered_quantity=qty,
                    unit_cost=cost_val,
                    planned_campaign_id=None
                ))

        po_obj.total_cost = round(po_tot, 2)

    # 9. Çalışanlar & Akademi Yetkinlikleri (Örnek Şube Kadroları)
    sample_employees = [
        Employee(employee_code="EMP_90124", full_name="Ahmet Yılmaz", store_id=stores[1].id, department="MEAT_AND_BUTCHERY", job_title="Reyon Kasap Sorumlusu"),
        Employee(employee_code="EMP_90125", full_name="Selin Aktaş", store_id=stores[1].id, department="CASH_DESK", job_title="Kasa Şefi"),
        Employee(employee_code="EMP_90126", full_name="Burak Demir", store_id=stores[2].id, department="FRUIT_VEG", job_title="Taze Meyve-Sebze Uzmanı"),
        Employee(employee_code="EMP_90127", full_name="Merve Can", store_id=stores[3].id, department="BAKERY", job_title="Fırın & Unlu Mamul Sorumlusu"),
        Employee(employee_code="EMP_90128", full_name="Murat Kaya", store_id=stores[4].id, department="MEAT_AND_BUTCHERY", job_title="Kasap Elemanı"),
    ]
    db.add_all(sample_employees)
    db.flush()

    sample_competencies = [
        EmployeeCompetency(employee_id=sample_employees[0].id, competency_code="MEAT_YIELD_MANAGEMENT", competency_name="Karkas Et Parçalama ve Randıman", score=72.0, operational_level="INTERMEDIATE"),
        EmployeeCompetency(employee_id=sample_employees[0].id, competency_code="HYGIENE_HACCP", competency_name="Gıda Güvenliği & Soğuk Zincir", score=88.0, operational_level="SENIOR"),
        EmployeeCompetency(employee_id=sample_employees[1].id, competency_code="CASHIER_SPEED", competency_name="Kasa Hızı & Barkod Ergonomisi", score=92.0, operational_level="MASTER"),
        EmployeeCompetency(employee_id=sample_employees[2].id, competency_code="FRESH_WASTE_MANAGEMENT", competency_name="Meyve-Sebze Fire ve Tasfiye Yönetimi", score=65.0, operational_level="NOVICE"),
        EmployeeCompetency(employee_id=sample_employees[3].id, competency_code="BAKERY_RECIPE_PLANNING", competency_name="Pişirme Reçetesi & Bayat Ekmek Kontrolü", score=78.0, operational_level="INTERMEDIATE"),
    ]
    db.add_all(sample_competencies)

    # 10. Örnek Başlangıç Aksiyon Kartları (Yönetici Kokpiti İçin)
    initial_actions = [
        ActionCard(
            card_code="ACT_INIT_001",
            source_module="SALES_LOSS",
            title="Süt Ürünleri Cirosunda %7 Düşüş (5 Şube)",
            description="Son 4 haftada süt grubunda ciro kaybı yaşandı. 14 kritik SKU'da bulunurluk kaybı tespit edildi.",
            root_cause="Depo-şube sevkiyat parametrelerinin güncellenmemesi ve güvenlik stoğu yetersizliği",
            financial_impact_try=820000.0,
            assigned_to="Ahmet Kılıç (Satın Alma / İkmal)",
            approver="Ticari Direktör",
            priority=ActionCardPriority.CRITICAL.value,
            status=ActionCardStatus.OPEN.value,
            deadline_date=date(2026, 9, 8),
            created_at=datetime.utcnow()
        ),
        ActionCard(
            card_code="ACT_INIT_002",
            source_module="AUDIT_FAIL",
            title="Şişli Şube Kasa-Raf Fiyat Uyuşmazlığı",
            description="Haftalık denetimde 6 temel gıda ürününde raf etiketi ile kasa fiyatı arasında fark saptandı.",
            root_cause="Yeni fiyat etiketlerinin akşam vardiyasında basılmaması",
            financial_impact_try=15000.0,
            assigned_to="Şişli Mağaza Müdürü",
            approver="Bölge Müdürü",
            priority=ActionCardPriority.HIGH.value,
            status=ActionCardStatus.IN_PROGRESS.value,
            deadline_date=date(2026, 9, 4),
            created_at=datetime.utcnow()
        )
    ]
    db.add_all(initial_actions)

    db.commit()
    print("Veritabanı zengin tohumlama başarıyla tamamlandı.")
