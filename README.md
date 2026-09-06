# marketyönetimi360 - Yerel Market Perakende İşletim Sistemi

**marketyönetimi360**, gıda perakende işletmeleri (bağımsız market & süpermarket zincirleri) için tüm operasyonel, finansal ve stratejik süreçleri tek bir platformda birleştiren yeni nesil Perakende İşletim Sistemidir.

---

## 🚀 Öne Çıkan Özellikler

### 1. 👑 Yönetim Özeti & Patron Kokpit Ekranı
- **12 Bloklu Stratejik Hiyerarşi:** Anomali Şeridi, Anlık Zincir Nabzı, Şube Kıyaslama, Kategori & Üretici Kârlılığı, Satınalma Masası, Sermaye & Stok Yükü, Risk & Kayıp Önleme, Otomatik Aksiyonlar ve BSC Bağlantısı.
- **4 Çeyreklik Karşılaştırma Matrisi (Q1, Q2, Q3, Q4, YTD & Geçen Yıl):** Ciro, Büyüme %, Gıda Enflasyonu, Reel Büyüme %, Brüt Marj %, GMROI, Müşteri Sayısı (Değişim %), Sepet Ortalaması (Değişim %) ve YGS Devir Hızı.
- **8 Boyutlu KPI Kıyaslama Masası:** Şubeler, Kategoriler, Üreticiler, Satınalmacılar, Hedef YGS, 3D GMROI, Space-to-Sales (m²) ve Büyüme Matrisi.
- **Toplantılar Karar Özeti:** Platform genelindeki tüm toplantı kararlarını ve aksiyon kayıtlarını tek merkezde toplayan konsolide salt-okunur rapor.
- **Yönetim Toplantıları:** İcra Kurulu (Çeyreklik), Satınalma & Kategori (Haftalık), Saha & Satış Değerlendirme (Haftalık) ve ortak **Aksiyon / Karar Kaydı** bileşeni.

### 2. 🛒 11 Bağımsız Ana Menü Mimarisi
1. **Yönetim Özeti & Patron Masası**
2. **Ticari Yönetim** (Akıllı Satın Alma, Tedarikçi Masası, Finansal Stok Yükü, Kampanyalar, Pazarlama & Marka)
3. **Tedarik Zinciri** (Talep Tahminleme, Stok & İkmal, Depo & Lojistik)
4. **Mağaza Yönetimi** (Mağazalar & Stok Sağlığı, Mağaza Karneleri, Fire & İmha, Denetimler, Müşteri Deneyimi & NPS)
5. **Finans Yönetimi** (Nakit Akış & Vade CCC, Konsolide P&L Kâr-Zarar)
6. **İnsan Kaynakları** (Norm Kadro, Vardiya Puantaj, Turnover, Eğitim & Sertifikasyon)
7. **Teknik Bakım** (Soğutucu Dolaplar & Klimalar, Jeneratör & Demirbaş, Arıza SLA)
8. **Bilgi Teknolojileri (IT)** (ERP & POS Entegrasyon, Rol & Yetki Matrisi, Güvenlik)
9. **Yatırım & Yeni Mağaza** (Lokasyon Fizibilitesi, Açılış Bütçesi CAPEX, Şube Kapanış/Devir)
10. **Risk ve Uyum** (HACCP Gıda Güvenliği, Kayıp Önleme & Sayım Farkı, Sözleşmeler, İSG & İş Kazası Defteri)
11. **Bağlı Platformlar** (XPlusCRM, Eğitim & Perakende Kariyer Akademisi, PerakendeData)

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10+
- Modern Web Tarayıcısı (Chrome, Edge, Firefox, Safari)

### Adımlar
```bash
# Sanal ortam oluşturma ve etkinleştirme
python -m venv venv
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yükleme
pip install -r requirements.txt

# Sunucuyu başlatma
python run_server.py
```

Tarayıcınızda açın: **`http://127.0.0.1:8000`**
API Dokümantasyonu (Swagger): **`http://127.0.0.1:8000/docs`**
