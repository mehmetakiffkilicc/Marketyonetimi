import sys
import io

# UTF-8 stdout wrapper for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_all_tests():
    print("--- 1. Health Check Testi ---")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] Health check basarili:", res.json())

    print("\n--- 2. Uretici Listesi & Karne Testi ---")
    sup_res = client.get("/api/v1/suppliers")
    assert sup_res.status_code == 200
    suppliers = sup_res.json()
    print(f"[OK] {len(suppliers)} adet tedarikci listelendi.")

    cards_res = client.get("/api/v1/suppliers/scorecards")
    assert cards_res.status_code == 200
    cards = cards_res.json()
    print(f"[OK] {len(cards)} tedarikci karnesi hesaplandi. Ornek Karne:")
    sample_card = cards[0]
    print(f"  - Tedarikci: {sample_card['supplier_name']}")
    print(f"  - Toplam Stok Degeri: {sample_card['total_stock_cost']:,.2f} TL")
    print(f"  - Son 3 Ay Satis Cirosu: {sample_card['total_revenue']:,.2f} TL (Ciro Payi: %{sample_card['revenue_share_pct']})")
    print(f"  - Brut Kar: {sample_card['gross_profit']:,.2f} TL (Kar Payi: %{sample_card['profit_share_pct']})")
    print(f"  - Yeter Gun Sayisi: {sample_card['days_of_inventory']} Gun ({sample_card['inventory_health']})")
    print(f"  - BCG Matris Sinifi: {sample_card['bcg_segment']}")

    print("\n--- 3. Satin Alma Workbench (Gecmis 3 Ay, Gelecek 3 Ay Tahmin, Kampanya) Testi ---")
    sutas_id = suppliers[0]["id"]
    wb_res = client.get(f"/api/v1/purchasing/workbench/{sutas_id}")
    assert wb_res.status_code == 200
    wb_data = wb_res.json()
    print(f"[OK] Tedarikci '{wb_data['supplier_name']}' icin {len(wb_data['items'])} urun workbench'e getirildi.")
    sample_item = wb_data["items"][0]
    print(f"  - Urun: {sample_item['product_name']} ({sample_item['barcode']})")
    print(f"  - Anlik Stok (Depo: {sample_item['central_warehouse_stock']}, Magazalar: {sample_item['total_stores_stock']})")
    print(f"  - Yeter Gun: {sample_item['days_of_inventory']} gun | Gunluk Satis Hizi: {sample_item['daily_run_rate']} adet/gun")
    print(f"  - Gecmis 3 Ay Satislari: {[m['month_label'] + ': ' + str(m['total_quantity']) + ' ad' for m in sample_item['past_3_months_sales']]}")
    print(f"  - Gelecek 3 Ay AI Tahmini: {[m['month_label'] + ': ' + str(m['total_forecast_qty']) + ' ad' for m in sample_item['forecast_3_months']]}")
    print(f"  - Onerilen Siparis: {sample_item['suggested_order_qty']} adet (Maliyet: {sample_item['suggested_order_qty'] * sample_item['purchase_price']:,.2f} TL)")

    print("\n--- 4. Siparis Aninda Kampanya Tanimlama & PO Olusturma Testi ---")
    po_payload = {
        "supplier_id": sutas_id,
        "buyer_id": 1,
        "expected_delivery_date": "2026-09-04",
        "notes": "15-20 Eylul Okul Acilisi Sut Kampanyasi Siparisi",
        "items": [
            {
                "product_id": sample_item["product_id"],
                "ordered_quantity": 500,
                "unit_cost": sample_item["purchase_price"],
                "planned_campaign": {
                    "product_id": sample_item["product_id"],
                    "title": "15-20 Eylul Okula Donus Sut Senligi",
                    "start_date": "2026-09-15",
                    "end_date": "2026-09-20",
                    "campaign_type": "PERCENT_DISCOUNT",
                    "discount_rate": 0.15,
                    "target_sales_qty": 500,
                    "target_revenue": 16750.0
                }
            }
        ]
    }
    po_res = client.post("/api/v1/purchasing/orders", json=po_payload)
    assert po_res.status_code == 200
    po_data = po_res.json()
    print("[OK] Siparis ve Entegre Kampanya basariyla olusturuldu:")
    print(f"  - PO No: {po_data['po_number']}, Toplam Tutar: {po_data['total_cost']:,.2f} TL")
    print(f"  - Bagli Kampanya Adedi: {po_data['linked_campaign_count']}")

    print("\n--- 5. Finansal Stok Yuku Testi (Kategori, Satin Almaci, Uretici & Vade Acigi) ---")
    fin_res = client.get("/api/v1/analytics/financial-burden")
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    print(f"[OK] Toplam Stok Maliyeti: {fin_data['total_inventory_cost']:,.2f} TL")
    print(f"[OK] Toplam Atil Stok Maliyeti (>45 Gun): {fin_data['total_idle_inventory_cost']:,.2f} TL")
    print("  - Satin Almaci Butce & Stok Kullanimi:")
    for b in fin_data["by_buyer"]:
        print(f"    * {b['buyer_name']}: Stok={b['current_stock_cost']:,.2f} TL (Butce: {b['monthly_budget_limit']:,.2f} TL, Kullanim: %{b['budget_utilization_pct']}), Atil={b['idle_stock_cost']:,.2f} TL")
    print("  - Uretici Vade Acigi / Nakit Kanamasi Riskleri:")
    for s in fin_data["by_supplier"][:4]:
        print(f"    * {s['supplier_name']}: Yeter Gun={s['days_of_inventory']}g, Vade={s['payment_term_days']}g -> Vade Acigi={s['maturity_gap_days']}g ({s['maturity_risk_status']})")

    print("\n--- 6. Depoda Var, Magazada Yok & Yok Satanlar (Lost Sales) Testi ---")
    gap_res = client.get("/api/v1/analytics/stockouts")
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    print(f"[OK] Ikmal Uyusmazligi Olan Urun Sayisi: {gap_data['gap_count']}")
    print(f"[OK] Tahmini Toplam Kayip Ciro: {gap_data['total_estimated_lost_revenue']:,.2f} TL")
    for gap in gap_data["warehouse_available_store_empty_items"]:
        print(f"  - [DEPODA VAR MAGAZADA YOK] {gap['product_name']}: Depo Stogu={gap['central_warehouse_stock']} ad. Stoksuz Subeler: {', '.join(gap['out_of_stock_stores'])} -> Onerilen Transfer: {gap['recommended_transfer_qty']} ad.")

    print("\n--- 7. XPlusCRM Entegrasyon Testi ---")
    # A. Simülasyon
    crm_sim_payload = {"store_id": 2, "product_id": 1, "max_discount_pct": 25.0}
    sim_res = client.post("/api/v1/crm/simulate-liquidation", json=crm_sim_payload)
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    print(f"[OK] CRM Tasfiye Simulasyonu: {sim_data['product_name']} ({sim_data['store_name']})")
    print(f"  - Fazla Stok: {sim_data['excess_stock_qty']} ad | Onerilen Fiyat: {sim_data['suggested_promo_price']} TL (Indirim: %{sim_data['discount_pct']})")
    print(f"  - Hedef Kitle: {sim_data['estimated_target_customers']} kisi | Tahmini Ciro: {sim_data['estimated_revenue_try']:,.2f} TL")

    # B. Kampanya Feedback Webhook
    feedback_payload = {
        "campaign_id": "cmp_test_oil_2026",
        "origin_event_id": "ACT_INIT_001",
        "targeted_customers": 450,
        "messages_delivered": 442,
        "coupons_redeemed_in_store": 128,
        "conversion_rate_pct": 28.96,
        "total_revenue_generated_try": 29440.0,
        "units_sold": 128,
        "remaining_excess_units": 12,
        "incremental_basket_revenue_try": 78200.0,
        "dominant_segment": "PREMIUM_FAMILY_SHOPPERS",
        "avg_total_basket_value_try": 610.93,
        "churn_prevented_customer_count": 31
    }
    fb_res = client.post("/api/v1/crm/campaign-feedback", json=feedback_payload)
    assert fb_res.status_code == 200
    print(f"[OK] XPlusCRM Kampanya Geri Bildirimi Basariyla Islendi: {fb_res.json()['message']}")

    # C. CRM Insights
    ins_res = client.get("/api/v1/crm/campaign-insights")
    assert ins_res.status_code == 200
    insights = ins_res.json()
    print(f"[OK] {len(insights)} CRM kampanya icgorusu getirildi.")

    print("\n--- 8. Perakende Kariyer Akademisi (HR Skills) Entegrasyon Testi ---")
    # A. Yetkinlik Matrisi
    matrix_res = client.get("/api/v1/hr/skills/matrix")
    assert matrix_res.status_code == 200
    matrix = matrix_res.json()
    print(f"[OK] {len(matrix)} calisan yetkinlik profili getirildi.")
    sample_emp = matrix[0]
    print(f"  - Calisan: {sample_emp['full_name']} ({sample_emp['job_title']} - {sample_emp['store_name']})")
    print(f"  - Yetkinlikler: {[c['competency_name'] + ' (' + str(c['score']) + ')' for c in sample_emp['competencies']]}")

    # B. Sertifika Doğrulama Webhook'u (Sertifika Tamamlama)
    cert_payload = {
        "certification_event_id": "CERT_TEST_8819",
        "employee_code": sample_emp["employee_code"],
        "course_code": "CRS_MEAT_YIELD_OPT_101",
        "course_name": "Karkas Et Randimani ve Fire Azaltma",
        "exam_score": 96.0,
        "passed": True,
        "certificate_qr_url": "https://certificates.perakendekariyer.com/verify/MEAT-90124",
        "skill_delta": {
            "competency_area": "MEAT_YIELD_MANAGEMENT",
            "previous_score": 72.0,
            "new_score": 96.0,
            "unlocked_operational_role": "MASTER_BUTCHER"
        }
    }
    cert_res = client.post("/api/v1/hr/skills/skill-verification", json=cert_payload)
    assert cert_res.status_code == 200
    print(f"[OK] Akademi Sertifikasi Dogrulandi: {cert_res.json()['message']}")

    print("\n--- 9. Tetikleyici Motoru ve Aksiyon Kartlari Testi ---")
    # A. Sistem Geneli Anomali Denetimi
    audit_res = client.post("/api/v1/triggers/run-audit")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    print(f"[OK] Kapsamli Anomali Denetimi Calistirildi:")
    print(f"  - Tespit Edilen Anomali: {audit_data['anomalies_detected_count']}")
    print(f"  - Olusturulan Aksiyon Karti: {audit_data['action_cards_created_count']}")
    print(f"  - XPlusCRM Tetikleyicisi: {audit_data['crm_events_dispatched_count']}")
    print(f"  - Akademi Egitim Atamasi: {audit_data['training_assignments_created_count']}")

    # B. Aksiyon Kartlarını Listeleme
    cards_res = client.get("/api/v1/triggers/action-cards")
    assert cards_res.status_code == 200
    action_cards = cards_res.json()
    print(f"[OK] Toplam {len(action_cards)} adet Aksiyon Karti mevcut.")
    for card in action_cards[:3]:
        print(f"  - [{card['priority']}] {card['title']} (Durum: {card['status']}, Etki: {card['financial_impact_try']:,.2f} TL)")

    # C. Aksiyon Kartı Kapatma
    first_open_card = [c for c in action_cards if c["status"] == "OPEN"][0]
    resolve_payload = {
        "resolution_evidence": "Depolar arasi transfer tamamlandi ve raf etiketleri guncellendi.",
        "actual_recovered_try": first_open_card["financial_impact_try"] * 0.9
    }
    resolve_res = client.post(f"/api/v1/triggers/action-cards/{first_open_card['id']}/resolve", json=resolve_payload)
    assert resolve_res.status_code == 200
    resolved_card = resolve_res.json()
    print(f"[OK] Aksiyon Karti Basariyla Kapatildi: '{resolved_card['title']}' -> Durum: {resolved_card['status']}, Geri Kazanim: {resolved_card['actual_recovered_try']:,.2f} TL")

    print("\n==========================================")
    print("TUM TESTLER (CRM, AKADEMI, TETIKLEYICILER DAHIL) BASARIYLA TAMAMLANDI! [OK]")
    print("==========================================")

if __name__ == "__main__":
    run_all_tests()

