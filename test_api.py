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
    print(f"  - Kar Marji: %{sample_card['gross_margin_pct']:.1f} (Kar Payi: %{sample_card['profit_share_pct']})")
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

    print("\n==========================================")
    print("TUM TESTLER BASARIYLA TAMAMLANDI! [OK]")
    print("==========================================")

if __name__ == "__main__":
    run_all_tests()
