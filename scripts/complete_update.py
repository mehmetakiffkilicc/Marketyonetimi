# -*- coding: utf-8 -*-
"""
Full Complete Implementation of MarketYonetimi360 UI & Components:
1. 11 Main Menus in Sidebar
2. Meeting Hubs (Icra [Quarterly], Purchasing [Monthly/Weekly], Field [Monthly/Weekly], Tracking)
3. Universal Action/Decision Component & Store (9 connected pages)
4. Read-only 'Toplantılar Karar Özeti' with 10 columns and 5-role filtering
5. New Sub-pages: Marketing, CX, P&L, Training Tracking, Permits, Work Accidents, Store Closing, Inventory Variance
"""
import os
import re

SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Sidebar
import sys
# Execute update_dashboard.py first
import subprocess
subprocess.run([sys.executable, "scripts/update_dashboard.py"], check=True)

# Re-read html
with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 2. Build New Sections HTML
new_sections_html = """
        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: TOPLANTILAR KARAR ÖZETİ (KONSOLİDE, SALT-OKUNUR RAPOR) -->
        <!-- ========================================================================= -->
        <section id="section-meetings-summary" class="space-y-6 hidden">
            <!-- Header -->
            <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 rounded-2xl shadow-md border border-indigo-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-amber-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">YÖNETİM ÖZETİ</span>
                        <span class="text-xs text-indigo-200/80 font-medium">• Konsolide İzleme Raporu</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        📋 Toplantılar ve Karar Özeti (Konsolide Rapor)
                    </h1>
                    <p class="text-xs text-indigo-200/80 mt-1">Platform genelindeki tüm toplantı ve süreç kararlarının tek merkezde toplandığı konsolide, salt-okunur denetim tablosu.</p>
                </div>
                <div class="flex items-center gap-2.5">
                    <span class="bg-indigo-500/20 text-indigo-300 text-xs px-3 py-1.5 rounded-xl border border-indigo-500/30 flex items-center gap-1.5 font-bold">
                        <i class="fa-solid fa-lock text-amber-400"></i> Salt-Okunur (Read-Only)
                    </span>
                    <button onclick="filterMeetingsSummary()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-3.5 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-rotate-right"></i> Yenile
                    </button>
                </div>
            </div>

            <!-- Salt-Okunur Bilgilendirme Uyarısı & Rol Simülatörü -->
            <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs text-blue-900 shadow-xs">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center text-sm shrink-0">
                        <i class="fa-solid fa-shield-halved"></i>
                    </div>
                    <div>
                        <div class="font-bold text-blue-950">Bilgi & Güvenlik Kuralı: Salt-Okunur Rapor</div>
                        <p class="text-blue-800 text-[11px] mt-0.5">Bu raporda doğrudan düzenleme yapılamaz. Karar durumu güncellemeleri yalnızca kaynak modüllerin (İcra Kurulu, Satınalma, Saha vb.) kendi sonuç tablolarından gerçekleştirilir.</p>
                    </div>
                </div>
                <!-- Rol Bazlı Görünürlük Simülatörü (Rol & Yetki Matrisi ile Bağlı) -->
                <div class="flex items-center gap-2 bg-white px-3 py-2 rounded-xl border border-blue-200 shrink-0">
                    <label class="font-bold text-slate-700 text-[11px] flex items-center gap-1"><i class="fa-solid fa-user-gear text-indigo-600"></i> Aktif Rol:</label>
                    <select id="summaryRoleSimulator" onchange="filterMeetingsSummary()" class="bg-slate-50 border border-slate-300 rounded-lg px-2 py-1 text-xs font-bold text-slate-800 cursor-pointer focus:ring-2 focus:ring-blue-500">
                        <option value="EXECUTIVE">👑 Genel Müdür / İcra Kurulu (Tüm Kayıtlar)</option>
                        <option value="FIELD_MANAGER">🏢 Bölge / Saha Müdürü (Saha + Mağaza Denetim)</option>
                        <option value="PURCHASING_MANAGER">🛒 Satınalma / Kategori Müdürü (Satınalma + PO)</option>
                        <option value="UNIT_RESPONSIBLE">👥 İK / Finans / Teknik Bakım Sorumlusu (Birim İçi)</option>
                        <option value="EMPLOYEE">👤 Genel Çalışan (Sadece Kendisine Atananlar)</option>
                    </select>
                </div>
            </div>

            <!-- Filtreleme Çubuğu (Kaynak Modül, Birim, Durum, Toplantı Dönemi, Tarih Aralığı, Sorumlu) -->
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Kaynak Modül</label>
                    <select id="sumFilterSource" onchange="filterMeetingsSummary()" class="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl p-2 font-semibold">
                        <option value="">Tüm Kaynaklar</option>
                        <option value="İcra Kurulu Toplantısı">İcra Kurulu Toplantısı</option>
                        <option value="Satınalma & Kategori Toplantısı">Satınalma & Kategori</option>
                        <option value="Saha & Satış Değerlendirme">Saha & Satış Değerlendirme</option>
                        <option value="Yeni Lokasyon Fizibilitesi">Yeni Lokasyon Fizibilitesi</option>
                        <option value="Şube Kapanış/Devir Değerlendirmesi">Şube Kapanış/Devir</option>
                        <option value="Ruhsat & Resmi İzin Takibi">Ruhsat & Resmi İzin</option>
                        <option value="İş Kazası Kayıt Defteri">İş Kazası Kayıt Defteri</option>
                        <option value="Bölge Müdürü Denetim Formu">Bölge Müdürü Denetimi</option>
                        <option value="Otomatik PO Onayları">Otomatik PO Onayları</option>
                        <option value="Açık Aksiyon Kartları">Açık Aksiyon Kartları</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Birim</label>
                    <select id="sumFilterUnit" onchange="filterMeetingsSummary()" class="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl p-2 font-semibold">
                        <option value="">Tüm Birimler</option>
                        <option value="İcra Kurulu">İcra Kurulu</option>
                        <option value="Satın Alma">Satın Alma</option>
                        <option value="Saha Operasyon">Saha Operasyon</option>
                        <option value="Finans">Finans</option>
                        <option value="İnsan Kaynakları">İnsan Kaynakları</option>
                        <option value="Teknik Bakım">Teknik Bakım</option>
                        <option value="Hukuk & Uyum">Hukuk & Uyum</option>
                        <option value="İSG">İSG</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Durum</label>
                    <select id="sumFilterStatus" onchange="filterMeetingsSummary()" class="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl p-2 font-semibold">
                        <option value="">Tüm Durumlar</option>
                        <option value="Yapıldı">✅ Yapıldı</option>
                        <option value="Yapılması Gerekiyor">⏳ Yapılması Gerekiyor</option>
                        <option value="Beklemede">⏸️ Beklemede</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Toplantı Dönemi</label>
                    <select id="sumFilterPeriod" onchange="filterMeetingsSummary()" class="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl p-2 font-semibold">
                        <option value="">Tüm Dönemler</option>
                        <option value="Q1">Q1</option>
                        <option value="Q2">Q2</option>
                        <option value="Q3">Q3</option>
                        <option value="Q4">Q4</option>
                        <option value="Eylül - Hafta 1">Eylül - Hafta 1</option>
                        <option value="Eylül - Hafta 2">Eylül - Hafta 2</option>
                        <option value="Eylül - Hafta 3">Eylül - Hafta 3</option>
                        <option value="Eylül - Hafta 4">Eylül - Hafta 4</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Sorumlu Kişi</label>
                    <select id="sumFilterAssignee" onchange="filterMeetingsSummary()" class="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl p-2 font-semibold">
                        <option value="">Tüm Sorumlular</option>
                        <option value="Ahmet Kılıç">Ahmet Kılıç</option>
                        <option value="Zeynep Turan">Zeynep Turan</option>
                        <option value="Mehmet Saygın">Mehmet Saygın</option>
                        <option value="Selin Vural">Selin Vural</option>
                        <option value="Ali Demir">Ali Demir</option>
                        <option value="Murat Kaya">Murat Kaya</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Arama</label>
                    <input type="text" id="sumFilterSearch" oninput="filterMeetingsSummary()" placeholder="Metin ara..." class="w-full bg-slate-50 border border-slate-200 text-xs rounded-xl p-2 font-semibold">
                </div>
            </div>

            <!-- Konsolide Read-Only Tablo (10 Kolon Sıralaması Eksiksiz) -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div class="p-4 border-b border-slate-100 flex items-center justify-between">
                    <div class="font-bold text-slate-800 text-xs flex items-center gap-2">
                        <i class="fa-solid fa-list-check text-indigo-600"></i>
                        <span>Konsolide Karar ve Aksiyon Kayıtları</span>
                        <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full text-[10px] font-extrabold" id="summaryCountBadge">0 Kayıt</span>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-slate-50/80 text-slate-500 font-bold border-b border-slate-200 text-[11px]">
                                <th class="p-3">Kaynak Modül</th>
                                <th class="p-3">Toplantı Dönemi</th>
                                <th class="p-3">Toplantı Tarihi</th>
                                <th class="p-3">Birim</th>
                                <th class="p-3">Aksiyon / Karar</th>
                                <th class="p-3">Sorumlu</th>
                                <th class="p-3">Başlangıç</th>
                                <th class="p-3">Bitiş</th>
                                <th class="p-3">Durum</th>
                                <th class="p-3">Sonuç / Gerekçe</th>
                            </tr>
                        </thead>
                        <tbody id="meetingsSummaryTableBody" class="divide-y divide-slate-100">
                            <!-- JS ile render edilir -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: İCRA KURULU TOPLANTISI (3 AYDA BİR / ÇEYREKLİK: Q1, Q2, Q3, Q4) -->
        <!-- ========================================================================= -->
        <section id="section-meetings-icra" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 p-6 rounded-2xl shadow-md border border-purple-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-purple-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">YÖNETİM TOPLANTILARI</span>
                        <span class="text-xs text-purple-200/80 font-medium">• Çeyreklik Stratejik Değerlendirme</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🏛️ İcra Kurulu Toplantısı (3 Ayda Bir / Çeyreklik)
                    </h1>
                    <p class="text-xs text-purple-200/80 mt-1">Genel strateji, zincir kârlılığı, CAPEX bütçesi ve çeyreklik icra kurulu kararları.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'İcra Kurulu Toplantısı', currentIcraQuarter, 'İcra Kurulu')" class="bg-purple-500 hover:bg-purple-400 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni İcra Kararı Ekle
                    </button>
                </div>
            </div>

            <!-- Q1 / Q2 / Q3 / Q4 Üst Navigasyon Sekmeleri -->
            <div class="flex items-center gap-2 bg-white p-2 rounded-2xl border border-slate-200 shadow-xs">
                <button onclick="switchIcraQuarter('Q1')" id="btn-icra-q1" class="icra-q-btn flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Q1 (Ocak - Mart)</button>
                <button onclick="switchIcraQuarter('Q2')" id="btn-icra-q2" class="icra-q-btn flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Q2 (Nisan - Haziran)</button>
                <button onclick="switchIcraQuarter('Q3')" id="btn-icra-q3" class="icra-q-btn flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all bg-purple-600 text-white shadow-xs">Q3 (Temmuz - Eylül) [Aktif]</button>
                <button onclick="switchIcraQuarter('Q4')" id="btn-icra-q4" class="icra-q-btn flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Q4 (Ekim - Aralık)</button>
            </div>

            <!-- Gündem Kartları & Metrikler -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Çeyreklik Konsolide Hedef</div>
                    <div class="text-xl font-extrabold text-purple-700 mt-1">36.5M TL Ciro / %28 Marj</div>
                    <div class="text-[10px] text-emerald-600 font-bold mt-1">Gerçekleşme Oranı: %102.4</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Ana Gündem Maddeleri</div>
                    <div class="text-xs font-bold text-slate-800 mt-1">1. Yeni Şube CAPEX Onayı</div>
                    <div class="text-xs font-bold text-slate-800">2. Tedarikçi Vade Açığı Önlemleri</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Toplantı Durumu</div>
                    <div class="text-xs font-extrabold text-emerald-600 mt-1">Tamamlandı & Kararlar Dağıtıldı</div>
                    <div class="text-[10px] text-slate-500">Tarih: 02.09.2026 | Saat: 10:00</div>
                </div>
            </div>

            <!-- İcra Kurulu Karar Tablosu (Ortak Bileşen Entegre) -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-bold text-slate-800 text-xs flex items-center gap-2">
                        <i class="fa-solid fa-gavel text-purple-600"></i>
                        <span id="icraTableTitle">Q3 İcra Kurulu Alınan Kararlar & Aksiyonlar</span>
                    </h3>
                </div>
                <div id="icraDecisionsTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: SATINALMA & KATEGORİ TOPLANTILARI (HAFTALIK / AY ÜST GRUPLU) -->
        <!-- ========================================================================= -->
        <section id="section-meetings-purchasing" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 p-6 rounded-2xl shadow-md border border-blue-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-blue-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">YÖNETİM TOPLANTILARI</span>
                        <span class="text-xs text-blue-200/80 font-medium">• Haftalık Kategori Masası</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🛒 Satınalma & Kategori Yönetimi Toplantıları
                    </h1>
                    <p class="text-xs text-blue-200/80 mt-1">Haftalık sipariş kotaları, tedarikçi fiyat artış onayları, insert ürünleri ve stok açığı değerlendirmesi.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'Satınalma & Kategori Toplantısı', `${currentPurchasingMonth} - ${currentPurchasingWeek}`, 'Satın Alma')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Satınalma Kararı Ekle
                    </button>
                </div>
            </div>

            <!-- Ay Seçici & Hafta Sekmeleri -->
            <div class="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs space-y-3">
                <div class="flex items-center gap-3">
                    <label class="text-xs font-bold text-slate-600 flex items-center gap-1.5"><i class="fa-regular fa-calendar text-blue-600"></i> Ay Seçimi:</label>
                    <select id="purchasingMonthSelect" onchange="changePurchasingMonth(this.value)" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-1.5 text-xs font-bold text-slate-800">
                        <option value="Ocak">Ocak</option>
                        <option value="Şubat">Şubat</option>
                        <option value="Mart">Mart</option>
                        <option value="Nisan">Nisan</option>
                        <option value="Mayıs">Mayıs</option>
                        <option value="Haziran">Haziran</option>
                        <option value="Temmuz">Temmuz</option>
                        <option value="Ağustos">Ağustos</option>
                        <option value="Eylül" selected>Eylül (Aktif)</option>
                        <option value="Ekim">Ekim</option>
                        <option value="Kasım">Kasım</option>
                        <option value="Aralık">Aralık</option>
                    </select>
                </div>
                <div class="flex items-center gap-2 border-t border-slate-100 pt-2">
                    <button onclick="switchPurchasingWeek('Hafta 1')" id="btn-pur-w1" class="pur-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all bg-blue-600 text-white shadow-xs">Hafta 1</button>
                    <button onclick="switchPurchasingWeek('Hafta 2')" id="btn-pur-w2" class="pur-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Hafta 2</button>
                    <button onclick="switchPurchasingWeek('Hafta 3')" id="btn-pur-w3" class="pur-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Hafta 3</button>
                    <button onclick="switchPurchasingWeek('Hafta 4')" id="btn-pur-w4" class="pur-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Hafta 4</button>
                </div>
            </div>

            <!-- Satınalma Karar Tablosu (Ortak Bileşen Entegre) -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-bold text-slate-800 text-xs flex items-center gap-2">
                        <i class="fa-solid fa-cart-flatbed text-blue-600"></i>
                        <span id="purchasingTableTitle">Eylül - Hafta 1 Satınalma Toplantı Kararları</span>
                    </h3>
                </div>
                <div id="purchasingDecisionsTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: SAHA & SATIŞ DEĞERLENDİRME TOPLANTISI (HAFTALIK / AY ÜST GRUPLU) -->
        <!-- ========================================================================= -->
        <section id="section-meetings-field" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 p-6 rounded-2xl shadow-md border border-teal-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-teal-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">YÖNETİM TOPLANTILARI</span>
                        <span class="text-xs text-teal-200/80 font-medium">• Saha & Mağaza Performansı</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🏬 Saha & Satış Değerlendirme Toplantısı
                    </h1>
                    <p class="text-xs text-teal-200/80 mt-1">Mağaza müdürleri ve bölge sorumluları ile haftalık ciro hedefleri, taze reyon kayıpları ve personel planı.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'Saha & Satış Değerlendirme', `${currentFieldMonth} - ${currentFieldWeek}`, 'Saha Operasyon')" class="bg-teal-600 hover:bg-teal-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Saha Kararı Ekle
                    </button>
                </div>
            </div>

            <!-- Ay Seçici & Hafta Sekmeleri -->
            <div class="bg-white p-3 rounded-2xl border border-slate-200 shadow-xs space-y-3">
                <div class="flex items-center gap-3">
                    <label class="text-xs font-bold text-slate-600 flex items-center gap-1.5"><i class="fa-regular fa-calendar text-teal-600"></i> Ay Seçimi:</label>
                    <select id="fieldMonthSelect" onchange="changeFieldMonth(this.value)" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-1.5 text-xs font-bold text-slate-800">
                        <option value="Ocak">Ocak</option>
                        <option value="Şubat">Şubat</option>
                        <option value="Mart">Mart</option>
                        <option value="Nisan">Nisan</option>
                        <option value="Mayıs">Mayıs</option>
                        <option value="Haziran">Haziran</option>
                        <option value="Temmuz">Temmuz</option>
                        <option value="Ağustos">Ağustos</option>
                        <option value="Eylül" selected>Eylül (Aktif)</option>
                        <option value="Ekim">Ekim</option>
                        <option value="Kasım">Kasım</option>
                        <option value="Aralık">Aralık</option>
                    </select>
                </div>
                <div class="flex items-center gap-2 border-t border-slate-100 pt-2">
                    <button onclick="switchFieldWeek('Hafta 1')" id="btn-fld-w1" class="fld-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all bg-teal-600 text-white shadow-xs">Hafta 1</button>
                    <button onclick="switchFieldWeek('Hafta 2')" id="btn-fld-w2" class="fld-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Hafta 2</button>
                    <button onclick="switchFieldWeek('Hafta 3')" id="btn-fld-w3" class="fld-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Hafta 3</button>
                    <button onclick="switchFieldWeek('Hafta 4')" id="btn-fld-w4" class="fld-w-btn flex-1 py-1.5 px-2 rounded-lg text-xs font-bold transition-all text-slate-600 hover:bg-slate-100">Hafta 4</button>
                </div>
            </div>

            <!-- Saha Karar Tablosu (Ortak Bileşen Entegre) -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-bold text-slate-800 text-xs flex items-center gap-2">
                        <i class="fa-solid fa-store text-teal-600"></i>
                        <span id="fieldTableTitle">Eylül - Hafta 1 Saha & Satış Toplantı Kararları</span>
                    </h3>
                </div>
                <div id="fieldDecisionsTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: TOPLANTI KARAR TAKİBİ (ORTAK BİLEŞEN İLE TÜM TOPLANTILAR) -->
        <!-- ========================================================================= -->
        <section id="section-meetings-tracking" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 p-6 rounded-2xl shadow-md border border-purple-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-purple-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">YÖNETİM TOPLANTILARI</span>
                        <span class="text-xs text-purple-200/80 font-medium">• Karar İcra Masası</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        📌 Toplantı Karar Takibi
                    </h1>
                    <p class="text-xs text-purple-200/80 mt-1">İcra Kurulu, Satınalma ve Saha toplantılarından çıkan kararların sorumlu, süre ve tamamlanma durumu takibi.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'Toplantı Karar Takibi', '', '')" class="bg-purple-600 hover:bg-purple-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Toplantı Kararı Aç
                    </button>
                </div>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div id="meetingsTrackingTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: PAZARLAMA & MARKA İLETİŞİMİ -->
        <!-- ========================================================================= -->
        <section id="section-marketing" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-pink-950 to-slate-900 p-6 rounded-2xl shadow-md border border-pink-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-pink-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">TİCARİ YÖNETİM</span>
                        <span class="text-xs text-pink-200/80 font-medium">• Pazarlama & Marka İletişimi</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        📢 Yerel Pazarlama, Sosyal Medya & Görsel Standartlar
                    </h1>
                    <p class="text-xs text-pink-200/80 mt-1">Şube lokasyon bazlı broşür ve dijital reklam takvimi, insert dağıtım denetimleri ve görsel marka kuralları.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Aktif Kampanya Broşürü</div>
                    <div class="text-2xl font-extrabold text-pink-600 mt-1">Eylül İnsert Kataloğu</div>
                    <div class="text-[10px] text-slate-500 font-medium">Baskı Adedi: 45.000 / Dağıtım: %98</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Yerel Sosyal Medya Erişimi</div>
                    <div class="text-2xl font-extrabold text-slate-900 mt-1">128.400 Kişi</div>
                    <div class="text-[10px] text-emerald-600 font-medium">+%18 Geçen Aya Göre</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Şube Görsel Standart Puanı</div>
                    <div class="text-2xl font-extrabold text-emerald-600 mt-1">92.4 / 100</div>
                    <div class="text-[10px] text-emerald-600 font-medium">Cephe, Tabela & Dönkart Uyumu</div>
                </div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: MÜŞTERİ DENEYİMİ (CX & NPS) -->
        <!-- ========================================================================= -->
        <section id="section-cx" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-rose-950 to-slate-900 p-6 rounded-2xl shadow-md border border-rose-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-rose-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">MAĞAZA YÖNETİMİ</span>
                        <span class="text-xs text-rose-200/80 font-medium">• Müşteri Deneyimi</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        ❤️ Müşteri Deneyimi, Şikayet Yönetimi ve NPS
                    </h1>
                    <p class="text-xs text-rose-200/80 mt-1">Müşteri geri bildirimleri, kasa kuyruk memnuniyeti, reyon temizliği ve Net Tavsiye Skoru (NPS).</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Zincir Geneli NPS Skoru</div>
                    <div class="text-2xl font-extrabold text-rose-600 mt-1">+68 NPS</div>
                    <div class="text-[10px] text-emerald-600 font-medium">Sektör Ortalaması: +52 (Mükemmel)</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Açık Müşteri Talebi</div>
                    <div class="text-2xl font-extrabold text-amber-600 mt-1">4 Talep</div>
                    <div class="text-[10px] text-amber-600 font-medium">Ortalama Çözüm Süresi: 2.1 Saat</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Kasa Bekleme Memnuniyeti</div>
                    <div class="text-2xl font-extrabold text-emerald-600 mt-1">%94.1</div>
                    <div class="text-[10px] text-slate-500 font-medium">Hızlı Kasa Açılış Kuralı Aktif</div>
                </div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: KÂR-ZARAR (P&L) KONSOLİDASYONU -->
        <!-- ========================================================================= -->
        <section id="section-pnl-consolidation" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-amber-950 to-slate-900 p-6 rounded-2xl shadow-md border border-amber-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-amber-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">FİNANS YÖNETİMİ</span>
                        <span class="text-xs text-amber-200/80 font-medium">• Finansal Özet</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        📊 Kâr-Zarar (P&L) Konsolidasyonu & Şirket Gelir Tablosu
                    </h1>
                    <p class="text-xs text-amber-200/80 mt-1">İşletme geneli konsolide finansal durum, brüt kâr, operasyonel giderler (OPEX), FAVÖK ve net kârlılık.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Konsolide Net Satışlar</div>
                    <div class="text-2xl font-extrabold text-slate-900 mt-1">34,554,800 TL</div>
                    <div class="text-[10px] text-emerald-600 font-medium">+%14.2 Büyüme (Yıllık)</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Brüt Kâr Marjı</div>
                    <div class="text-2xl font-extrabold text-emerald-600 mt-1">%28.4</div>
                    <div class="text-[10px] text-slate-500 font-medium">Tutar: 9,813,563 TL</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">FAVÖK (EBITDA)</div>
                    <div class="text-2xl font-extrabold text-blue-600 mt-1">%11.2</div>
                    <div class="text-[10px] text-slate-500 font-medium">Tutar: 3,870,137 TL</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Net Kâr Marjı</div>
                    <div class="text-2xl font-extrabold text-purple-600 mt-1">%6.8</div>
                    <div class="text-[10px] text-emerald-600 font-medium">Tutar: 2,349,726 TL</div>
                </div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: EĞİTİM & SERTİFİKASYON TAKİBİ -->
        <!-- ========================================================================= -->
        <section id="section-training-tracking" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 p-6 rounded-2xl shadow-md border border-sky-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-sky-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">İNSAN KAYNAKLARI</span>
                        <span class="text-xs text-sky-200/80 font-medium">• Akademi Entegre Gelişim</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🎓 Eğitim ve Sertifikasyon Takibi
                    </h1>
                    <p class="text-xs text-sky-200/80 mt-1">Perakende Kariyer Akademisi bağlantılı personel zorunlu kurs tamamlama, fire azaltma ve hijyen sertifikasyonları.</p>
                </div>
                <div>
                    <button onclick="switchTab('academy')" class="bg-sky-500 hover:bg-sky-400 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-graduation-cap"></i> Kariyer Akademisine Git
                    </button>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Aktif Sertifikalı Personel</div>
                    <div class="text-2xl font-extrabold text-sky-600 mt-1">76 / 84 Kişi</div>
                    <div class="text-[10px] text-emerald-600 font-medium">Sertifikasyon Oranı: %90.4</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Devam Eden Zorunlu Eğitimler</div>
                    <div class="text-2xl font-extrabold text-amber-600 mt-1">3 Eğitim</div>
                    <div class="text-[10px] text-amber-600 font-medium">Karkas Et Randımanı & Soğuk Zincir</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Eğitim Sonrası Fire Kazanımı</div>
                    <div class="text-2xl font-extrabold text-emerald-600 mt-1">29,250 TL / Ay</div>
                    <div class="text-[10px] text-emerald-600 font-medium">Ölçülen Maliyet İyileşmesi</div>
                </div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: RUHSAT & RESMİ İZİN TAKİBİ -->
        <!-- ========================================================================= -->
        <section id="section-permits" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 p-6 rounded-2xl shadow-md border border-blue-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-blue-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">RİSK VE UYUM</span>
                        <span class="text-xs text-blue-200/80 font-medium">• Resmi Belgeler Masası</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🏛️ Ruhsat & Resmi İzin Takibi
                    </h1>
                    <p class="text-xs text-blue-200/80 mt-1">Belediye işyeri açma ruhsatları, TAPDK tütün/alkol izinleri, itfaiye uygunluk ve baca denetim belgeleri.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'Ruhsat & Resmi İzin Takibi', '', 'Hukuk & Uyum')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni İzin / Ruhsat Aksiyonu Ekle
                    </button>
                </div>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div id="permitsTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: İŞ KAZASI KAYIT DEFTERİ -->
        <!-- ========================================================================= -->
        <section id="section-work-accidents" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-rose-950 to-slate-900 p-6 rounded-2xl shadow-md border border-rose-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-rose-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">RİSK VE UYUM</span>
                        <span class="text-xs text-rose-200/80 font-medium">• İş Sağlığı ve Güvenliği</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🦺 İş Kazası Kayıt Defteri & İSG Aksiyonları
                    </h1>
                    <p class="text-xs text-rose-200/80 mt-1">Mağaza ve depolardaki ramak kala olayları, iş kazası bildirimleri, kök neden analizi ve düzeltici İSG aksiyonları.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'İş Kazası Kayıt Defteri', '', 'İSG')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni İSG Olayı / Aksiyonu Ekle
                    </button>
                </div>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div id="workAccidentsTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: ŞUBE KAPANIŞ / DEVİR DEĞERLENDİRMESİ -->
        <!-- ========================================================================= -->
        <section id="section-store-closing" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 p-6 rounded-2xl shadow-md border border-purple-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-purple-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">YATIRIM VE YENİ MAĞAZA</span>
                        <span class="text-xs text-purple-200/80 font-medium">• Verimsiz Şube Tasfiye</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        🚪 Şube Kapanış ve Devir Değerlendirmesi
                    </h1>
                    <p class="text-xs text-purple-200/80 mt-1">Sürekli zarar eden veya kira artışı nedeniyle verimsizleşen şubelerin tasfiye, devir, stok tahliye ve personel transfer aksiyonları.</p>
                </div>
                <div>
                    <button onclick="openActionDecisionModal('', 'Şube Kapanış/Devir Değerlendirmesi', '', 'Yatırım & Proje')" class="bg-purple-600 hover:bg-purple-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Kapanış/Devir Kararı Ekle
                    </button>
                </div>
            </div>

            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4">
                <div id="storeClosingTableContainer"></div>
            </div>
        </section>

        <!-- ========================================================================= -->
        <!-- 🆕 SECTION: ENVANTER SAYIM FARKI ANALİZİ -->
        <!-- ========================================================================= -->
        <section id="section-inventory-variance" class="space-y-6 hidden">
            <div class="bg-gradient-to-r from-slate-900 via-rose-950 to-slate-900 p-6 rounded-2xl shadow-md border border-rose-900/50 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-rose-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-wider">RİSK VE UYUM</span>
                        <span class="text-xs text-rose-200/80 font-medium">• Envanter Denetimi</span>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        📦 Envanter Sayım Farkı Analizi
                    </h1>
                    <p class="text-xs text-rose-200/80 mt-1">Genel sayım ve kısmi sayım sonuçları, sayım açık/fazlaları, kategori bazlı kayıp oranları ve mutabakat raporları.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Son Genel Sayım Doğruluğu</div>
                    <div class="text-2xl font-extrabold text-emerald-600 mt-1">%99.12</div>
                    <div class="text-[10px] text-slate-500 font-medium">Hedef: %98.5+</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">Toplam Sayım Açığı Tutar</div>
                    <div class="text-2xl font-extrabold text-rose-600 mt-1">14,820 TL</div>
                    <div class="text-[10px] text-slate-500 font-medium">5 Şube + 1 Ana Depo Toplamı</div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div class="text-[10px] font-bold text-slate-400 uppercase">En Yüksek Fark Olan Kategori</div>
                    <div class="text-2xl font-extrabold text-amber-600 mt-1">Kozmetik & Bakım</div>
                    <div class="text-[10px] text-amber-600 font-medium">Güvenlik Etiketi Kontrolü Başlatıldı</div>
                </div>
            </div>
        </section>
"""

# Insert new sections right before `<!-- SECTION: CATEGORY & SKU MANAGEMENT -->`
cat_pos = html.find('<!-- SECTION: CATEGORY & SKU MANAGEMENT -->')
if cat_pos != -1:
    html = html[:cat_pos] + new_sections_html + "\n\n        " + html[cat_pos:]
    print("New sections inserted successfully!")
else:
    print("Warning: cat_pos not found!")

# 3. Add Modal for Universal Action / Decision Log (if not already present)
modal_action_decision_html = """
    <!-- ========================================================================= -->
    <!-- 🆕 MODAL: EVRENSEL AKSİYON / KARAR KAYDI FORMU -->
    <!-- ========================================================================= -->
    <div id="modalActionDecision" class="fixed inset-0 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center z-50 hidden p-4">
        <div class="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center text-sm font-bold shadow-xs">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </div>
                    <div>
                        <h3 class="font-extrabold text-slate-900 text-base" id="modalActionDecisionTitle">Aksiyon / Karar Kaydı</h3>
                        <p class="text-[11px] text-slate-500">Platform geneli standart karar yönetim bileşeni</p>
                    </div>
                </div>
                <button onclick="closeActionDecisionModal()" class="text-slate-400 hover:text-slate-700 text-lg w-8 h-8 rounded-xl hover:bg-slate-100 flex items-center justify-center transition-colors">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <form id="formActionDecision" onsubmit="event.preventDefault(); saveActionDecisionRecord();" class="space-y-4 text-xs">
                <input type="hidden" id="adId" value="">

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Kaynak Modül</label>
                        <input type="text" id="adSourceModule" required class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Birim / Departman</label>
                        <select id="adUnit" required class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                            <option value="İcra Kurulu">İcra Kurulu</option>
                            <option value="Satın Alma">Satın Alma</option>
                            <option value="Saha Operasyon">Saha Operasyon</option>
                            <option value="Finans">Finans</option>
                            <option value="İnsan Kaynakları">İnsan Kaynakları</option>
                            <option value="Teknik Bakım">Teknik Bakım</option>
                            <option value="Hukuk & Uyum">Hukuk & Uyum</option>
                            <option value="İSG">İSG</option>
                            <option value="Yatırım & Proje">Yatırım & Proje</option>
                            <option value="İç Denetim">İç Denetim</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Toplantı Dönemi <span class="text-slate-400 font-normal">(Toplantı dışıysa "—")</span></label>
                        <input type="text" id="adPeriod" placeholder="örn: Q3 2026 veya Eylül - Hafta 1 veya —" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Toplantı Tarihi <span class="text-slate-400 font-normal">(Opsiyonel)</span></label>
                        <input type="date" id="adMeetingDate" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                    </div>
                </div>

                <div>
                    <label class="block font-bold text-slate-700 mb-1">Aksiyon / Alınan Karar Tanımı</label>
                    <textarea id="adActionDecision" required rows="2" placeholder="Alınan kararın veya icra edilecek aksiyonun net tanımı..." class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800"></textarea>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Sorumlu Kişi</label>
                        <select id="adAssignee" required class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                            <option value="Ahmet Kılıç">Ahmet Kılıç (Satın Alma)</option>
                            <option value="Zeynep Turan">Zeynep Turan (Kategori)</option>
                            <option value="Mehmet Saygın">Mehmet Saygın (Finans)</option>
                            <option value="Selin Vural">Selin Vural (İK)</option>
                            <option value="Ali Demir">Ali Demir (Saha)</option>
                            <option value="Murat Kaya">Murat Kaya (Reyon)</option>
                            <option value="Caner Öz">Caner Öz (Teknik)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Başlangıç Tarihi</label>
                        <input type="date" id="adStartDate" required class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Bitiş Tarihi (Hedef)</label>
                        <input type="date" id="adEndDate" required class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">Durum</label>
                        <select id="adStatus" onchange="onActionStatusChange(this.value)" required class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-bold text-slate-800">
                            <option value="Yapıldı">✅ Yapıldı</option>
                            <option value="Yapılması Gerekiyor" selected>⏳ Yapılması Gerekiyor</option>
                            <option value="Beklemede">⏸️ Beklemede</option>
                        </select>
                    </div>
                    <div>
                        <!-- Durum = Yapıldı ise 'Sonuç', diğerlerinde 'Gerekçe' etiketi -->
                        <label id="adResultReasonLabel" class="block font-bold text-slate-700 mb-1">Gerekçe (Tamamlanmama / Gecikme Sebebi)</label>
                        <textarea id="adResultReason" rows="2" placeholder="Gerekçe veya açıklama giriniz..." class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-800"></textarea>
                    </div>
                </div>

                <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
                    <button type="button" onclick="closeActionDecisionModal()" class="px-4 py-2 rounded-xl text-slate-600 bg-slate-100 hover:bg-slate-200 font-bold transition-colors">Vazgeç</button>
                    <button type="submit" class="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-black shadow-sm transition-colors flex items-center gap-1.5">
                        <i class="fa-solid fa-check"></i> Kaydet
                    </button>
                </div>
            </form>
        </div>
    </div>
"""

# Insert modal before `</body>`
if '<div id="modalActionDecision"' not in html:
    body_pos = html.find('</body>')
    html = html[:body_pos] + modal_action_decision_html + "\n" + html[body_pos:]
    print("Modal inserted successfully!")

# 4. Universal Action/Decision Store & Logic Engine in JS
action_js_engine = """
        // =========================================================================
        // 🆕 EVRENSEL AKSİYON / KARAR VERİ MODELİ VE MOTORU (ActionDecisionStore)
        // =========================================================================
        let currentIcraQuarter = 'Q3';
        let currentPurchasingMonth = 'Eylül';
        let currentPurchasingWeek = 'Hafta 1';
        let currentFieldMonth = 'Eylül';
        let currentFieldWeek = 'Hafta 1';

        let actionDecisionStore = [
            {
                id: 1,
                sourceModule: "İcra Kurulu Toplantısı",
                period: "Q3",
                meetingDate: "2026-09-02",
                unit: "İcra Kurulu",
                actionDecision: "Ataşehir yeni mağaza açılış CAPEX bütçesinin 4.5M TL olarak onaylanması ve kira sözleşmesinin imzalanması",
                assignee: "Ahmet Kılıç",
                startDate: "2026-09-02",
                endDate: "2026-09-20",
                status: "Yapıldı",
                resultReason: "Kira sözleşmesi imzalandı ve mimari proje ruhsat onayına sunuldu."
            },
            {
                id: 2,
                sourceModule: "İcra Kurulu Toplantısı",
                period: "Q3",
                meetingDate: "2026-09-02",
                unit: "İcra Kurulu",
                actionDecision: "Tedarikçi vade açığını kapatmak için Sütaş ve Unilever ile 15 gün ek vade müzakeresi yürütülmesi",
                assignee: "Zeynep Turan",
                startDate: "2026-09-03",
                endDate: "2026-09-30",
                status: "Yapılması Gerekiyor",
                resultReason: "Tedarikçi finans direktörleriyle toplantı takvimi belirleniyor."
            },
            {
                id: 3,
                sourceModule: "Satınalma & Kategori Toplantısı",
                period: "Eylül - Hafta 1",
                meetingDate: "2026-09-01",
                unit: "Satın Alma",
                actionDecision: "Eti Nero bisküvi stok tükenme riski nedeniyle 10.000 adetlik otomatik PO siparişinin onaylanması",
                assignee: "Ahmet Kılıç",
                startDate: "2026-09-01",
                endDate: "2026-09-05",
                status: "Yapıldı",
                resultReason: "PO-2026-0011 oluşturuldu, depoya sevk planı onaylandı."
            },
            {
                id: 4,
                sourceModule: "Satınalma & Kategori Toplantısı",
                period: "Eylül - Hafta 1",
                meetingDate: "2026-09-01",
                unit: "Satın Alma",
                actionDecision: "Maliyet artışı talep eden sıvı yağ tedarikçisi ile fiyat dondurma pazarlığı yapılması",
                assignee: "Zeynep Turan",
                startDate: "2026-09-02",
                endDate: "2026-09-10",
                status: "Beklemede",
                resultReason: "Piyasa zeytinyağı borsa fiyat bülteni bekleniyor."
            },
            {
                id: 5,
                sourceModule: "Saha & Satış Değerlendirme",
                period: "Eylül - Hafta 1",
                meetingDate: "2026-09-03",
                unit: "Saha Operasyon",
                actionDecision: "Kadıköy ve Beşiktaş şubelerinde boş kalan süt ve deterjan reyonlarına merkez depodan 40'ar koli acil transfer sevk edilmesi",
                assignee: "Ali Demir",
                startDate: "2026-09-03",
                endDate: "2026-09-04",
                status: "Yapıldı",
                resultReason: "Sevkiyat tamamlandı, mağaza reyon doluluk oranı %98'e ulaştı."
            },
            {
                id: 6,
                sourceModule: "Ruhsat & Resmi İzin Takibi",
                period: "—",
                meetingDate: "—",
                unit: "Hukuk & Uyum",
                actionDecision: "Beşiktaş Şube TAPDK tütün ve alkol satış izin belgesinin yıllık yenileme harcının yatırılması",
                assignee: "Mehmet Saygın",
                startDate: "2026-09-05",
                endDate: "2026-09-25",
                status: "Yapılması Gerekiyor",
                resultReason: "Belediye ve Tarım İlçe randevusu alındı."
            },
            {
                id: 7,
                sourceModule: "İş Kazası Kayıt Defteri",
                period: "—",
                meetingDate: "—",
                unit: "İSG",
                actionDecision: "Mal kabul rampasında kayma riskine karşı zemin kaydırmaz bant çekilmesi ve çelik burunlu ayakkabı denetimi",
                assignee: "Caner Öz",
                startDate: "2026-09-02",
                endDate: "2026-09-08",
                status: "Yapıldı",
                resultReason: "Tüm depoya zemin bantları uygulandı ve KKD tutanağı imzalatıldı."
            },
            {
                id: 8,
                sourceModule: "Yeni Lokasyon Fizibilitesi",
                period: "—",
                meetingDate: "—",
                unit: "Yatırım & Proje",
                actionDecision: "Maltepe Sahil lokasyonu yaya trafiği ve rakip market fiyat endeksi saha sayımının tamamlanması",
                assignee: "Ahmet Kılıç",
                startDate: "2026-09-04",
                endDate: "2026-09-18",
                status: "Yapılması Gerekiyor",
                resultReason: "Saha sayım ekibi 3 gün sürecek trafik analizini yürütüyor."
            },
            {
                id: 9,
                sourceModule: "Şube Kapanış/Devir Değerlendirmesi",
                period: "—",
                meetingDate: "—",
                unit: "Yatırım & Proje",
                actionDecision: "Zarar eden Üsküdar mini şubenin tasfiyesi yerine devir opsiyonu için yerel perakendeci ile görüşülmesi",
                assignee: "Mehmet Saygın",
                startDate: "2026-09-01",
                endDate: "2026-09-30",
                status: "Beklemede",
                resultReason: "Alıcı firmanın mali bilanço incelemesi devam ediyor."
            },
            {
                id: 10,
                sourceModule: "Bölge Müdürü Denetim Formu",
                period: "Eylül - Hafta 1",
                meetingDate: "2026-09-03",
                unit: "Saha Operasyon",
                actionDecision: "Kadıköy Şube kasap reyonu karkas et parçalama randımanını artırmak için personele zorunlu akademi eğitimi tanımlanması",
                assignee: "Murat Kaya",
                startDate: "2026-09-03",
                endDate: "2026-09-12",
                status: "Yapıldı",
                resultReason: "Eğitim tamamlandı, sertifika onaylandı ve fire %7.3 azaldı."
            },
            {
                id: 11,
                sourceModule: "Otomatik PO Onayları",
                period: "—",
                meetingDate: "—",
                unit: "Satın Alma",
                actionDecision: "Sütaş 1LT süt siparişi PO-2026-0012 için 45 gün vade onayı ve sevkiyat tamamlama",
                assignee: "Ahmet Kılıç",
                startDate: "2026-09-04",
                endDate: "2026-09-06",
                status: "Yapıldı",
                resultReason: "Tedarikçi portalına sipariş iletildi."
            }
        ];

        // Duruma göre etiket değiştirici (Yapıldı -> Sonuç, diğerleri -> Gerekçe)
        function onActionStatusChange(statusVal) {
            const labelEl = document.getElementById('adResultReasonLabel');
            const textareaEl = document.getElementById('adResultReason');
            if (!labelEl || !textareaEl) return;

            if (statusVal === 'Yapıldı') {
                labelEl.innerText = 'Sonuç (Elde Edilen Çıktı / Etki)';
                textareaEl.placeholder = 'Karar neticesinde elde edilen somut çıktı, tasarruf veya etkiyi yazınız...';
            } else if (statusVal === 'Beklemede') {
                labelEl.innerText = 'Gerekçe (Bekleme / Erteleme Sebebi)';
                textareaEl.placeholder = 'Kararın beklemede kalma veya gecikme sebebini yazınız...';
            } else {
                labelEl.innerText = 'Gerekçe (Tamamlanmama / Aksiyon Sebebi)';
                textareaEl.placeholder = 'Uygulama süreci veya planlanan adımları yazınız...';
            }
        }

        function openActionDecisionModal(id = '', defaultModule = '', defaultPeriod = '', defaultUnit = '', defaultAssignee = '') {
            const modal = document.getElementById('modalActionDecision');
            const titleEl = document.getElementById('modalActionDecisionTitle');
            if (!modal) return;

            document.getElementById('formActionDecision').reset();
            document.getElementById('adId').value = id || '';

            if (id) {
                const item = actionDecisionStore.find(x => x.id === parseInt(id));
                if (item) {
                    titleEl.innerText = `Aksiyon / Karar Düzenle #${item.id}`;
                    document.getElementById('adSourceModule').value = item.sourceModule || '';
                    document.getElementById('adUnit').value = item.unit || 'Satın Alma';
                    document.getElementById('adPeriod').value = item.period || '—';
                    document.getElementById('adMeetingDate').value = item.meetingDate !== '—' ? item.meetingDate : '';
                    document.getElementById('adActionDecision').value = item.actionDecision || '';
                    document.getElementById('adAssignee').value = item.assignee || 'Ahmet Kılıç';
                    document.getElementById('adStartDate').value = item.startDate || '';
                    document.getElementById('adEndDate').value = item.endDate || '';
                    document.getElementById('adStatus').value = item.status || 'Yapılması Gerekiyor';
                    document.getElementById('adResultReason').value = item.resultReason || '';
                    onActionStatusChange(item.status);
                }
            } else {
                titleEl.innerText = 'Yeni Aksiyon / Karar Kaydı';
                document.getElementById('adSourceModule').value = defaultModule || 'Yönetim Toplantıları';
                document.getElementById('adPeriod').value = defaultPeriod || '—';
                document.getElementById('adUnit').value = defaultUnit || 'Satın Alma';
                document.getElementById('adAssignee').value = defaultAssignee || 'Ahmet Kılıç';
                document.getElementById('adStartDate').value = new Date().toISOString().split('T')[0];
                const targetDate = new Date();
                targetDate.setDate(targetDate.getDate() + 7);
                document.getElementById('adEndDate').value = targetDate.toISOString().split('T')[0];
                document.getElementById('adStatus').value = 'Yapılması Gerekiyor';
                onActionStatusChange('Yapılması Gerekiyor');
            }

            modal.classList.remove('hidden');
        }

        function closeActionDecisionModal() {
            const modal = document.getElementById('modalActionDecision');
            if (modal) modal.classList.add('hidden');
        }

        function saveActionDecisionRecord() {
            const idVal = document.getElementById('adId').value;
            const sourceModule = document.getElementById('adSourceModule').value.trim();
            const unit = document.getElementById('adUnit').value;
            const period = document.getElementById('adPeriod').value.trim() || '—';
            const meetingDate = document.getElementById('adMeetingDate').value || '—';
            const actionDecision = document.getElementById('adActionDecision').value.trim();
            const assignee = document.getElementById('adAssignee').value;
            const startDate = document.getElementById('adStartDate').value;
            const endDate = document.getElementById('adEndDate').value;
            const status = document.getElementById('adStatus').value;
            const resultReason = document.getElementById('adResultReason').value.trim();

            if (idVal) {
                const idx = actionDecisionStore.findIndex(x => x.id === parseInt(idVal));
                if (idx !== -1) {
                    actionDecisionStore[idx] = {
                        ...actionDecisionStore[idx],
                        sourceModule, unit, period, meetingDate, actionDecision, assignee, startDate, endDate, status, resultReason
                    };
                    showToast(`Aksiyon / Karar #${idVal} başarıyla güncellendi!`, "success");
                }
            } else {
                const newId = actionDecisionStore.length > 0 ? Math.max(...actionDecisionStore.map(x => x.id)) + 1 : 1;
                actionDecisionStore.unshift({
                    id: newId,
                    sourceModule, unit, period, meetingDate, actionDecision, assignee, startDate, endDate, status, resultReason
                });
                showToast(`Yeni karar #${newId} başarıyla kaydedildi!`, "success");
            }

            closeActionDecisionModal();
            refreshAllConnectedActionTables();
        }

        function updateActionDecisionStatus(id, newStatus) {
            const item = actionDecisionStore.find(x => x.id === parseInt(id));
            if (item) {
                item.status = newStatus;
                showToast(`Karar #${id} durumu '${newStatus}' olarak güncellendi.`, "info");
                refreshAllConnectedActionTables();
            }
        }

        // Genel Yeniden Kullanılabilir Tablo Render Fonksiyonu
        function renderActionDecisionTable(containerId, filterFn, options = {}) {
            const container = document.getElementById(containerId);
            if (!container) return;

            let records = actionDecisionStore;
            if (typeof filterFn === 'function') {
                records = actionDecisionStore.filter(filterFn);
            }

            if (records.length === 0) {
                container.innerHTML = `
                    <div class="p-8 text-center text-slate-400 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
                        <i class="fa-solid fa-clipboard-list text-3xl text-slate-300 mb-2"></i>
                        <p class="font-bold text-xs">Bu kriterlere uygun açık veya kayıtlı karar bulunamadı.</p>
                    </div>`;
                return;
            }

            const allowEdit = options.readOnly !== true;

            const rowsHtml = records.map(r => {
                const statusBadge = r.status === 'Yapıldı' 
                    ? '<span class="bg-emerald-100 text-emerald-800 border border-emerald-300 px-2 py-0.5 rounded-full font-bold text-[10px]"><i class="fa-solid fa-check mr-1"></i>Yapıldı</span>'
                    : r.status === 'Beklemede'
                    ? '<span class="bg-amber-100 text-amber-800 border border-amber-300 px-2 py-0.5 rounded-full font-bold text-[10px]"><i class="fa-solid fa-pause mr-1"></i>Beklemede</span>'
                    : '<span class="bg-blue-100 text-blue-800 border border-blue-300 px-2 py-0.5 rounded-full font-bold text-[10px]"><i class="fa-solid fa-hourglass-half mr-1"></i>Yapılması Gerekiyor</span>';

                const resultLabel = r.status === 'Yapıldı' 
                    ? '<span class="text-emerald-700 font-bold">Sonuç: </span>' 
                    : '<span class="text-slate-500 font-bold">Gerekçe: </span>';

                return `
                    <tr class="hover:bg-slate-50/80 transition-colors">
                        <td class="p-3 font-bold text-slate-800">
                            <div>${r.actionDecision}</div>
                            <div class="text-[10px] text-slate-400 font-normal mt-0.5">${r.sourceModule} ${r.period && r.period !== '—' ? `• ${r.period}` : ''}</div>
                        </td>
                        <td class="p-3 whitespace-nowrap"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md font-semibold text-[10px]">${r.unit}</span></td>
                        <td class="p-3 whitespace-nowrap font-medium text-slate-700"><i class="fa-solid fa-user-tie text-blue-500 mr-1 text-[10px]"></i>${r.assignee}</td>
                        <td class="p-3 whitespace-nowrap text-slate-500 text-[11px]">${r.startDate} &rarr; <span class="font-bold text-slate-700">${r.endDate}</span></td>
                        <td class="p-3 whitespace-nowrap">${statusBadge}</td>
                        <td class="p-3 text-[11px] text-slate-600 max-w-xs">
                            ${resultLabel}<span>${r.resultReason || '—'}</span>
                        </td>
                        ${allowEdit ? `
                        <td class="p-3 whitespace-nowrap text-right">
                            <div class="flex items-center justify-end gap-1">
                                <button onclick="openActionDecisionModal(${r.id})" class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer" title="Düzenle">
                                    <i class="fa-solid fa-pen-to-square"></i>
                                </button>
                                ${r.status !== 'Yapıldı' ? `
                                <button onclick="updateActionDecisionStatus(${r.id}, 'Yapıldı')" class="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors cursor-pointer" title="Tamamlandı Olarak İşaretle">
                                    <i class="fa-solid fa-check-double"></i>
                                </button>` : ''}
                            </div>
                        </td>` : ''}
                    </tr>`;
            }).join('');

            container.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-slate-50/80 text-slate-500 font-bold border-b border-slate-200 text-[11px]">
                                <th class="p-3">Aksiyon / Karar</th>
                                <th class="p-3">Birim</th>
                                <th class="p-3">Sorumlu</th>
                                <th class="p-3">Süre</th>
                                <th class="p-3">Durum</th>
                                <th class="p-3">Sonuç / Gerekçe</th>
                                ${allowEdit ? '<th class="p-3 text-right">İşlem</th>' : ''}
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            ${rowsHtml}
                        </tbody>
                    </table>
                </div>`;
        }

        // =========================================================================
        // 🆕 KONSOLİDE RAPOR: TOPLANTILAR KARAR ÖZETİ FİLTRELEME & ROL MOTORU
        // =========================================================================
        function filterMeetingsSummary() {
            const role = document.getElementById('summaryRoleSimulator')?.value || 'EXECUTIVE';
            const source = document.getElementById('sumFilterSource')?.value || '';
            const unit = document.getElementById('sumFilterUnit')?.value || '';
            const status = document.getElementById('sumFilterStatus')?.value || '';
            const period = document.getElementById('sumFilterPeriod')?.value || '';
            const assignee = document.getElementById('sumFilterAssignee')?.value || '';
            const search = (document.getElementById('sumFilterSearch')?.value || '').toLowerCase().trim();

            let filtered = actionDecisionStore.filter(r => {
                // 1. Rol Bazlı Yetki Filtrelemesi
                if (role === 'FIELD_MANAGER') {
                    const allowedSources = ['Saha & Satış Değerlendirme', 'Bölge Müdürü Denetim Formu'];
                    const allowedUnits = ['Saha Operasyon', 'İç Denetim'];
                    if (!allowedSources.includes(r.sourceModule) && !allowedUnits.includes(r.unit)) return false;
                } else if (role === 'PURCHASING_MANAGER') {
                    const allowedSources = ['Satınalma & Kategori Toplantısı', 'Otomatik PO Onayları'];
                    const allowedUnits = ['Satın Alma'];
                    if (!allowedSources.includes(r.sourceModule) && !allowedUnits.includes(r.unit)) return false;
                } else if (role === 'UNIT_RESPONSIBLE') {
                    const allowedUnits = ['İnsan Kaynakları', 'Finans', 'Teknik Bakım'];
                    if (!allowedUnits.includes(r.unit)) return false;
                } else if (role === 'EMPLOYEE') {
                    if (r.assignee !== 'Ahmet Kılıç') return false; // Giriş yapmış varsayılan kullanıcı
                }

                // 2. Dropdown ve Arama Filtreleri
                if (source && r.sourceModule !== source) return false;
                if (unit && r.unit !== unit) return false;
                if (status && r.status !== status) return false;
                if (period && r.period !== period && !r.period.includes(period)) return false;
                if (assignee && r.assignee !== assignee) return false;
                if (search && !r.actionDecision.toLowerCase().includes(search) && !r.resultReason.toLowerCase().includes(search)) return false;

                return true;
            });

            // Count badge
            const badge = document.getElementById('summaryCountBadge');
            if (badge) badge.innerText = `${filtered.length} Kayıt Gösteriliyor`;

            // Render Table (Tam 10 Kolon Sıralaması, Salt-Okunur)
            const tbody = document.getElementById('meetingsSummaryTableBody');
            if (!tbody) return;

            if (filtered.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="p-8 text-center text-slate-400">
                            <i class="fa-solid fa-filter-circle-xmark text-2xl mb-1"></i>
                            <div class="font-bold">Seçilen rol ve filtre kriterlerine uygun kayıt bulunamadı.</div>
                        </td>
                    </tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(r => {
                const statusBadge = r.status === 'Yapıldı' 
                    ? '<span class="bg-emerald-100 text-emerald-800 border border-emerald-300 px-2 py-0.5 rounded-full font-bold text-[10px] whitespace-nowrap"><i class="fa-solid fa-check mr-1"></i>Yapıldı</span>'
                    : r.status === 'Beklemede'
                    ? '<span class="bg-amber-100 text-amber-800 border border-amber-300 px-2 py-0.5 rounded-full font-bold text-[10px] whitespace-nowrap"><i class="fa-solid fa-pause mr-1"></i>Beklemede</span>'
                    : '<span class="bg-blue-100 text-blue-800 border border-blue-300 px-2 py-0.5 rounded-full font-bold text-[10px] whitespace-nowrap"><i class="fa-solid fa-hourglass-half mr-1"></i>Yapılması Gerekiyor</span>';

                const resultLabel = r.status === 'Yapıldı' 
                    ? '<span class="text-emerald-700 font-extrabold">[Sonuç] </span>' 
                    : '<span class="text-amber-700 font-extrabold">[Gerekçe] </span>';

                return `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-bold text-slate-800 whitespace-nowrap">${r.sourceModule}</td>
                        <td class="p-3 whitespace-nowrap text-slate-600 font-medium">${r.period || '—'}</td>
                        <td class="p-3 whitespace-nowrap text-slate-500">${r.meetingDate || '—'}</td>
                        <td class="p-3 whitespace-nowrap"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md font-semibold text-[10px]">${r.unit}</span></td>
                        <td class="p-3 font-semibold text-slate-900 min-w-[220px]">${r.actionDecision}</td>
                        <td class="p-3 whitespace-nowrap font-medium text-slate-700">${r.assignee}</td>
                        <td class="p-3 whitespace-nowrap text-slate-500">${r.startDate}</td>
                        <td class="p-3 whitespace-nowrap font-bold text-slate-700">${r.endDate}</td>
                        <td class="p-3 whitespace-nowrap">${statusBadge}</td>
                        <td class="p-3 text-[11px] text-slate-600 min-w-[200px]">${resultLabel}${r.resultReason || '—'}</td>
                    </tr>`;
            }).join('');
        }

        // =========================================================================
        // 🆕 TOPLANTI GEÇİŞ FONKSİYONLARI (İCRA KURULU, SATINALMA, SAHA)
        // =========================================================================
        function switchIcraQuarter(quarter) {
            currentIcraQuarter = quarter;
            document.querySelectorAll('.icra-q-btn').forEach(b => {
                b.classList.remove('bg-purple-600', 'text-white', 'shadow-xs');
                b.classList.add('text-slate-600');
            });
            const btn = document.getElementById(`btn-icra-${quarter.toLowerCase()}`);
            if (btn) {
                btn.classList.remove('text-slate-600');
                btn.classList.add('bg-purple-600', 'text-white', 'shadow-xs');
            }
            const title = document.getElementById('icraTableTitle');
            if (title) title.innerText = `${quarter} İcra Kurulu Alınan Kararlar & Aksiyonlar`;

            renderActionDecisionTable('icraDecisionsTableContainer', r => r.sourceModule === 'İcra Kurulu Toplantısı' && r.period === quarter);
        }

        function changePurchasingMonth(monthVal) {
            currentPurchasingMonth = monthVal;
            updatePurchasingMeetingView();
        }

        function switchPurchasingWeek(weekVal) {
            currentPurchasingWeek = weekVal;
            document.querySelectorAll('.pur-w-btn').forEach(b => {
                b.classList.remove('bg-blue-600', 'text-white', 'shadow-xs');
                b.classList.add('text-slate-600');
            });
            const btnIdx = weekVal === 'Hafta 1' ? 1 : weekVal === 'Hafta 2' ? 2 : weekVal === 'Hafta 3' ? 3 : 4;
            const btn = document.getElementById(`btn-pur-w${btnIdx}`);
            if (btn) {
                btn.classList.remove('text-slate-600');
                btn.classList.add('bg-blue-600', 'text-white', 'shadow-xs');
            }
            updatePurchasingMeetingView();
        }

        function updatePurchasingMeetingView() {
            const periodStr = `${currentPurchasingMonth} - ${currentPurchasingWeek}`;
            const title = document.getElementById('purchasingTableTitle');
            if (title) title.innerText = `${periodStr} Satınalma Toplantı Kararları`;

            renderActionDecisionTable('purchasingDecisionsTableContainer', r => r.sourceModule === 'Satınalma & Kategori Toplantısı' && (r.period === periodStr || r.period.includes(currentPurchasingMonth)));
        }

        function changeFieldMonth(monthVal) {
            currentFieldMonth = monthVal;
            updateFieldMeetingView();
        }

        function switchFieldWeek(weekVal) {
            currentFieldWeek = weekVal;
            document.querySelectorAll('.fld-w-btn').forEach(b => {
                b.classList.remove('bg-teal-600', 'text-white', 'shadow-xs');
                b.classList.add('text-slate-600');
            });
            const btnIdx = weekVal === 'Hafta 1' ? 1 : weekVal === 'Hafta 2' ? 2 : weekVal === 'Hafta 3' ? 3 : 4;
            const btn = document.getElementById(`btn-fld-w${btnIdx}`);
            if (btn) {
                btn.classList.remove('text-slate-600');
                btn.classList.add('bg-teal-600', 'text-white', 'shadow-xs');
            }
            updateFieldMeetingView();
        }

        function updateFieldMeetingView() {
            const periodStr = `${currentFieldMonth} - ${currentFieldWeek}`;
            const title = document.getElementById('fieldTableTitle');
            if (title) title.innerText = `${periodStr} Saha & Satış Toplantı Kararları`;

            renderActionDecisionTable('fieldDecisionsTableContainer', r => r.sourceModule === 'Saha & Satış Değerlendirme' && (r.period === periodStr || r.period.includes(currentFieldMonth)));
        }

        // Tüm bağlı tabloları yenileme
        function refreshAllConnectedActionTables() {
            filterMeetingsSummary();
            switchIcraQuarter(currentIcraQuarter);
            updatePurchasingMeetingView();
            updateFieldMeetingView();
            renderActionDecisionTable('meetingsTrackingTableContainer', r => r.sourceModule.includes('Toplantı') || r.sourceModule.includes('İcra') || r.sourceModule.includes('Saha'));
            renderActionDecisionTable('permitsTableContainer', r => r.sourceModule === 'Ruhsat & Resmi İzin Takibi');
            renderActionDecisionTable('workAccidentsTableContainer', r => r.sourceModule === 'İş Kazası Kayıt Defteri');
            renderActionDecisionTable('storeClosingTableContainer', r => r.sourceModule === 'Şube Kapanış/Devir Değerlendirmesi');
        }
"""

# Insert JS Engine before switchTab
if 'ActionDecisionStore' not in html:
    switch_tab_pos = html.find('function switchTab(tabId)')
    if switch_tab_pos != -1:
        html = html[:switch_tab_pos] + action_js_engine + "\n\n        " + html[switch_tab_pos:]
        print("Action JS Engine inserted successfully!")
    else:
        print("Warning: switchTab pos not found!")

# 5. Extend switchTab to support all new tabs
old_switch_tab = """        // Tab Switcher for Sections
        function switchTab(tabId) {
            document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
            
            let secId = tabId;
            if (tabId === 'purchasing') secId = 'workbench';
            if (tabId === 'loss') secId = 'audit';
            if (tabId === 'strategy') secId = 'executive';
            if (tabId === 'kpis') secId = 'macro';
            
            const targetSec = document.getElementById(`section-${secId}`);
            if (targetSec) targetSec.classList.remove('hidden');

            if (tabId === 'executive') loadExecutiveDashboard();
            if (tabId === 'workbench' || tabId === 'purchasing') loadPurchasingWorkbench();
            if (tabId === 'stores') loadStoreInventoryHealth();
            if (tabId === 'suppliers') setTimeout(() => loadSupplierScorecards(), 50);
            if (tabId === 'burden') loadFinancialBurden();
            if (tabId === 'stockouts') loadStockouts();
            if (tabId === 'campaigns') loadCampaigns();
            if (tabId === 'orders') loadPurchaseOrdersReport();
            if (tabId === 'actions') loadActionCards();
            if (tabId === 'crm') loadCrmHub();
            if (tabId === 'academy') loadStoreSkillMatrix();
        }"""

new_switch_tab = """        // Tab Switcher for Sections
        function switchTab(tabId) {
            document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
            
            let secId = tabId;
            if (tabId === 'purchasing') secId = 'workbench';
            if (tabId === 'loss') secId = 'audit';
            if (tabId === 'strategy') secId = 'executive';
            if (tabId === 'kpis') secId = 'macro';
            if (tabId === 'po-approvals') secId = 'orders';
            if (tabId === 'store-audits') secId = 'audit';
            if (tabId === 'actions-resolved') secId = 'actions';
            
            const targetSec = document.getElementById(`section-${secId}`);
            if (targetSec) targetSec.classList.remove('hidden');

            if (tabId === 'executive') loadExecutiveDashboard();
            if (tabId === 'workbench' || tabId === 'purchasing') loadPurchasingWorkbench();
            if (tabId === 'stores') loadStoreInventoryHealth();
            if (tabId === 'suppliers') setTimeout(() => loadSupplierScorecards(), 50);
            if (tabId === 'burden') loadFinancialBurden();
            if (tabId === 'stockouts') loadStockouts();
            if (tabId === 'campaigns') loadCampaigns();
            if (tabId === 'orders' || tabId === 'po-approvals') loadPurchaseOrdersReport();
            if (tabId === 'actions' || tabId === 'actions-resolved') loadActionCards();
            if (tabId === 'crm') loadCrmHub();
            if (tabId === 'academy') loadStoreSkillMatrix();

            // 🆕 New Hubs
            if (tabId === 'meetings-summary') filterMeetingsSummary();
            if (tabId === 'meetings-icra') switchIcraQuarter(currentIcraQuarter);
            if (tabId === 'meetings-purchasing') updatePurchasingMeetingView();
            if (tabId === 'meetings-field') updateFieldMeetingView();
            if (tabId === 'meetings-tracking') renderActionDecisionTable('meetingsTrackingTableContainer', r => r.sourceModule.includes('Toplantı') || r.sourceModule.includes('İcra') || r.sourceModule.includes('Saha'));
            if (tabId === 'permits') renderActionDecisionTable('permitsTableContainer', r => r.sourceModule === 'Ruhsat & Resmi İzin Takibi');
            if (tabId === 'work-accidents') renderActionDecisionTable('workAccidentsTableContainer', r => r.sourceModule === 'İş Kazası Kayıt Defteri');
            if (tabId === 'store-closing') renderActionDecisionTable('storeClosingTableContainer', r => r.sourceModule === 'Şube Kapanış/Devir Değerlendirmesi');
        }"""

if old_switch_tab in html:
    html = html.replace(old_switch_tab, new_switch_tab)
    print("switchTab updated successfully!")
else:
    print("Warning: old_switch_tab exact string not found, updating via regex")
    html = re.sub(r'function switchTab\(tabId\) \{.*?if \(tabId === \'academy\'\) loadStoreSkillMatrix\(\);\s*\}', new_switch_tab, html, flags=re.DOTALL)

# Write out completed dashboard.html
with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Full Complete Dashboard Update Successfully Applied!")
