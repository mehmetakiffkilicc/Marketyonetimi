# -*- coding: utf-8 -*-
import os, re

def update_patron_cockpit():
    with open('app/templates/dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. New section-executive HTML
    exec_html = """            <!-- SECTION 0: EXECUTIVE (PATRON / GENEL MÜDÜR / CEO) COCKPIT -->
            <section id="section-executive" class="space-y-6">
                <!-- Top Executive Header -->
                <div class="bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 p-6 rounded-3xl shadow-xl border border-indigo-900/40 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2 mb-1.5">
                            <span class="bg-gradient-to-r from-amber-400 to-amber-500 text-slate-950 text-[10px] font-black px-2.5 py-0.5 rounded-full uppercase tracking-wider shadow-xs">👑 PATRON & GENEL MÜDÜR KOKPİTİ</span>
                            <span class="text-xs text-indigo-200/80 font-medium">• Şirket Stratejik Karar ve Sermaye Masası</span>
                        </div>
                        <h1 class="text-2xl lg:text-3xl font-black tracking-tight text-white flex items-center gap-2.5">
                            Market Zinciri Konsolide Yönetim Paneli
                        </h1>
                        <p class="text-xs text-indigo-200/80 mt-1 max-w-3xl">Dönem karşılaştırmaları, Gıda Enflasyonu vs Reel Büyüme, Personel & Metrekare Verimliliği, 3 Boyutlu GMROI, Kategori Hedef YGS Analizi ve AI Stratejik Patron Karar Masası.</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2.5">
                        <button onclick="exportPatronCockpitPDF()" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer" title="Patron Yönetim Raporunu PDF Olarak İndir">
                            <i class="fa-solid fa-file-pdf"></i> PDF Rapor
                        </button>
                        <button onclick="exportPatronCockpitExcel()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer" title="Patron Verilerini Excel Olarak İndir">
                            <i class="fa-solid fa-file-excel"></i> Excel İndir
                        </button>
                        <button onclick="loadExecutiveDashboard()" class="bg-white/10 hover:bg-white/20 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors border border-white/20 cursor-pointer">
                            <i class="fa-solid fa-rotate-right"></i> Yenile
                        </button>
                    </div>
                </div>

                <!-- Executive Dynamic Filters Bar -->
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div class="flex flex-wrap items-center gap-3 flex-1">
                        <!-- Dönem Seçici -->
                        <div class="min-w-[180px] flex-1">
                            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                                <i class="fa-solid fa-calendar-days text-indigo-600"></i> Dönem Karşılaştırması:
                            </label>
                            <select id="execPeriodFilter" onchange="loadExecutiveDashboard()" class="w-full bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-xl p-2 font-bold focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer">
                                <option value="YOY_2026_2025">📅 2026 vs 2025 (Yıllık Kıyaslama)</option>
                                <option value="YTD">📊 YTD (Yılbaşından Bugüne)</option>
                                <option value="Q3">📈 Q3 (Son 3 Ay Konsolide)</option>
                                <option value="MONTHLY">🗓️ Ağustos 2026 (Son Ay)</option>
                            </select>
                        </div>

                        <!-- 1. Mağazalar / Şubeler Menüsü -->
                        <div class="min-w-[170px] flex-1">
                            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                                <i class="fa-solid fa-store text-cyan-600"></i> Mağaza / Şube:
                            </label>
                            <select id="execStoreFilter" onchange="loadExecutiveDashboard()" class="w-full bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-xl p-2 font-bold focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer">
                                <option value="">🏪 Tüm Mağazalar (Zincir Geneli)</option>
                            </select>
                        </div>

                        <!-- 2. Satın Alma Müdürü Menüsü -->
                        <div class="min-w-[170px] flex-1">
                            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                                <i class="fa-solid fa-user-tie text-blue-600"></i> Satın Alma Müdürü:
                            </label>
                            <select id="execBuyerFilter" onchange="loadExecutiveDashboard()" class="w-full bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-xl p-2 font-bold focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer">
                                <option value="">👔 Tüm Satın Almacılar</option>
                            </select>
                        </div>

                        <!-- 3. Üretici / Tedarikçi Firma Menüsü -->
                        <div class="min-w-[170px] flex-1">
                            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                                <i class="fa-solid fa-industry text-indigo-600"></i> Üretici / Tedarikçi:
                            </label>
                            <select id="execSupplierFilter" onchange="loadExecutiveDashboard()" class="w-full bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-xl p-2 font-bold focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer">
                                <option value="">🏭 Tüm Üretici Firmalar</option>
                            </select>
                        </div>

                        <!-- 4. Kategori Menüsü -->
                        <div class="min-w-[150px] flex-1">
                            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                                <i class="fa-solid fa-layer-group text-purple-600"></i> Kategori:
                            </label>
                            <select id="execCategoryFilter" onchange="loadExecutiveDashboard()" class="w-full bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-xl p-2 font-bold focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer">
                                <option value="">🏷️ Tüm Kategoriler</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex items-center gap-2 self-end md:self-center">
                        <button onclick="resetExecutiveFilters()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors border border-slate-200 cursor-pointer">
                            <i class="fa-solid fa-filter-circle-xmark text-slate-500"></i> Sıfırla
                        </button>
                    </div>
                </div>

                <!-- 👑 MASTER KPI CARDS GRID (6 BÜYÜK YÖNETİCİ KARTI) -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
                    <!-- 1. Nominal Ciro & YoY Büyüme -->
                    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs hover:border-blue-400 transition-all">
                        <div class="flex justify-between items-center text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            <span>Satış Cirosu (Bu Yıl)</span>
                            <i class="fa-solid fa-turkish-lira-sign text-blue-600 text-xs"></i>
                        </div>
                        <div class="text-xl lg:text-2xl font-black text-slate-900 mt-1" id="execKpiRevenue">₺0</div>
                        <div class="text-[10px] text-emerald-600 font-bold mt-1 flex items-center gap-1">
                            <i class="fa-solid fa-arrow-trend-up"></i> <span id="execKpiRevenueGrowth">%+34.0 Büyüme</span>
                        </div>
                        <div class="text-[9px] text-slate-400 mt-0.5 truncate" id="execKpiPriorRevenue">Geçen Yıl: ₺0</div>
                    </div>

                    <!-- 2. Adetsel Satış Hacmi & Büyüme -->
                    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs hover:border-cyan-400 transition-all">
                        <div class="flex justify-between items-center text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            <span>Satış Hacmi (Adet)</span>
                            <i class="fa-solid fa-boxes-stacked text-cyan-600 text-xs"></i>
                        </div>
                        <div class="text-xl lg:text-2xl font-black text-slate-900 mt-1" id="execKpiQty">0 Adet</div>
                        <div class="text-[10px] text-emerald-600 font-bold mt-1 flex items-center gap-1">
                            <i class="fa-solid fa-arrow-trend-up"></i> <span id="execKpiQtyGrowth">%+6.4 Hacim Artışı</span>
                        </div>
                        <div class="text-[9px] text-slate-400 mt-0.5 truncate" id="execKpiPriorQty">Geçen Yıl: 0 Adet</div>
                    </div>

                    <!-- 3. Gıda Enflasyonu vs Reel Büyüme -->
                    <div class="bg-white p-4 rounded-2xl border border-rose-200 shadow-xs bg-rose-50/20 hover:border-rose-400 transition-all">
                        <div class="flex justify-between items-center text-rose-800 text-[10px] font-bold uppercase tracking-wider">
                            <span>Reel Büyüme Oranı</span>
                            <i class="fa-solid fa-arrow-trend-down text-rose-600 text-xs"></i>
                        </div>
                        <div class="text-xl lg:text-2xl font-black text-rose-600 mt-1" id="execKpiRealGrowth">-%2.4</div>
                        <div class="text-[10px] text-rose-700 font-bold mt-1 flex items-center gap-1">
                            <span>TÜİK Gıda Enflasyonu: %36.4</span>
                        </div>
                        <div class="text-[9px] text-rose-600 mt-0.5 font-medium">⚠️ Enflasyon erozyonu var</div>
                    </div>

                    <!-- 4. Sektör Karşılaştırması -->
                    <div class="bg-white p-4 rounded-2xl border border-amber-200 shadow-xs bg-amber-50/20 hover:border-amber-400 transition-all">
                        <div class="flex justify-between items-center text-amber-800 text-[10px] font-bold uppercase tracking-wider">
                            <span>Sektörel Pazar Payı</span>
                            <i class="fa-solid fa-chart-line text-amber-600 text-xs"></i>
                        </div>
                        <div class="text-xl lg:text-2xl font-black text-amber-700 mt-1" id="execKpiMarketShare">-4.2 Puan</div>
                        <div class="text-[10px] text-slate-700 font-bold mt-1">
                            Sektör: %38.2 • Biz: %34.0
                        </div>
                        <div class="text-[9px] text-amber-700 mt-0.5 font-medium">Sektör ortalaması altında</div>
                    </div>

                    <!-- 5. Personel & m² Verimliliği -->
                    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs hover:border-indigo-400 transition-all">
                        <div class="flex justify-between items-center text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            <span>Personel & Alan Verimi</span>
                            <i class="fa-solid fa-users text-indigo-600 text-xs"></i>
                        </div>
                        <div class="text-lg lg:text-xl font-black text-indigo-950 mt-1" id="execKpiStaffProd">₺0 / Kişi</div>
                        <div class="text-[10px] text-indigo-700 font-bold mt-1" id="execKpiSqmProd">
                            m² Verimi: ₺0 / m²
                        </div>
                        <div class="text-[9px] text-slate-400 mt-0.5">84 Personel • 2.450 m² Alan</div>
                    </div>

                    <!-- 6. Müşteri & Sepet Derinliği -->
                    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs hover:border-emerald-400 transition-all">
                        <div class="flex justify-between items-center text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            <span>Sepet & Müşteri</span>
                            <i class="fa-solid fa-basket-shopping text-emerald-600 text-xs"></i>
                        </div>
                        <div class="text-xl lg:text-2xl font-black text-emerald-700 mt-1" id="execKpiBasketAvg">₺0</div>
                        <div class="text-[10px] text-emerald-800 font-bold mt-1" id="execKpiCustomerCount">
                            0 Fiş • 5.2 Parça
                        </div>
                        <div class="text-[9px] text-slate-400 mt-0.5" id="execKpiPriorBasket">Geçen Yıl: ₺185.00</div>
                    </div>
                </div>

                <!-- 📊 İKİ BÜYÜK PANEL: BRÜT KÂRLILIK & STOK SERMAYESİ YGS -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Sol Panel: Brüt Kârlılık Hedef vs Gerçekleşen -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
                        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                            <div class="flex items-center gap-2">
                                <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                                    <i class="fa-solid fa-chart-pie"></i>
                                </div>
                                <div>
                                    <h3 class="font-black text-slate-900 text-sm">Brüt Kârlılık (Hedef vs Gerçekleşen)</h3>
                                    <p class="text-[10px] text-slate-500">Konsolide Kâr Tutarı ve Marj Sapma Analizi</p>
                                </div>
                            </div>
                            <span class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2.5 py-1 rounded-full">HEDEF AŞILDI ✅</span>
                        </div>

                        <div class="grid grid-cols-3 gap-3 text-center">
                            <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                                <div class="text-[10px] text-slate-400 font-bold uppercase">Hedef Kâr Marjı</div>
                                <div class="text-lg font-black text-slate-700 mt-0.5">%28.0</div>
                                <div class="text-[9px] text-slate-400" id="execTargetProfitTry">Hedef: ₺0</div>
                            </div>
                            <div class="bg-emerald-50/70 p-3 rounded-xl border border-emerald-100">
                                <div class="text-[10px] text-emerald-700 font-bold uppercase">Gerçekleşen Kâr</div>
                                <div class="text-lg font-black text-emerald-700 mt-0.5" id="execActualMargin">%29.8</div>
                                <div class="text-[9px] text-emerald-700 font-bold" id="execActualProfitVal">₺0</div>
                            </div>
                            <div class="bg-blue-50/70 p-3 rounded-xl border border-blue-100">
                                <div class="text-[10px] text-blue-700 font-bold uppercase">Kâr Fazlası / Sapma</div>
                                <div class="text-lg font-black text-blue-700 mt-0.5" id="execProfitVariancePct">+%1.8</div>
                                <div class="text-[9px] text-blue-700 font-bold" id="execProfitVarianceTry">+₺621.051</div>
                            </div>
                        </div>

                        <!-- Progress Bar -->
                        <div>
                            <div class="flex justify-between text-[11px] font-bold mb-1">
                                <span class="text-slate-600">Kâr Gerçekleşme Oranı</span>
                                <span class="text-emerald-700 font-extrabold" id="execProfitRealizationPct">%106.4</span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                                <div class="bg-emerald-500 h-full rounded-full" style="width: 100%;"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Sağ Panel: Stok Sermayesi, GMROI ve Hedef YGS -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
                        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                            <div class="flex items-center gap-2">
                                <div class="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                                    <i class="fa-solid fa-cubes-stacked"></i>
                                </div>
                                <div>
                                    <h3 class="font-black text-slate-900 text-sm">Stok Sermayesi, YGS ve GMROI</h3>
                                    <p class="text-[10px] text-slate-500">Stok Yeter Gün Sayısı ve Fazla Sermaye Yükü</p>
                                </div>
                            </div>
                            <span class="bg-amber-100 text-amber-800 text-[10px] font-black px-2.5 py-1 rounded-full">4.4 GÜN FAZLA STOK ⚠️</span>
                        </div>

                        <div class="grid grid-cols-3 gap-3 text-center">
                            <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                                <div class="text-[10px] text-slate-400 font-bold uppercase">Hedef YGS</div>
                                <div class="text-lg font-black text-slate-700 mt-0.5">14.0 Gün</div>
                                <div class="text-[9px] text-slate-400">İdeal İkmal Süresi</div>
                            </div>
                            <div class="bg-amber-50/70 p-3 rounded-xl border border-amber-100">
                                <div class="text-[10px] text-amber-800 font-bold uppercase">Mevcut Fiili YGS</div>
                                <div class="text-lg font-black text-amber-800 mt-0.5" id="execActualYgs">18.4 Gün</div>
                                <div class="text-[9px] text-amber-700 font-bold" id="execActualStockCostVal">₺0 Stok</div>
                            </div>
                            <div class="bg-purple-50/70 p-3 rounded-xl border border-purple-100">
                                <div class="text-[10px] text-purple-800 font-bold uppercase">Konsolide GMROI</div>
                                <div class="text-lg font-black text-purple-800 mt-0.5" id="execActualGmroiVal">3.11x</div>
                                <div class="text-[9px] text-purple-700 font-bold">₺1 Stok = ₺3.11 Kâr</div>
                            </div>
                        </div>

                        <!-- Excess Capital Alert -->
                        <div class="p-3 bg-amber-50/90 rounded-xl border border-amber-200 flex items-center justify-between">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-triangle-exclamation text-amber-600 text-sm"></i>
                                <div>
                                    <div class="text-xs font-bold text-amber-900">Bağlı Fazla Stok Sermayesi (YGS > 14g)</div>
                                    <div class="text-[10px] text-amber-700">Bu tutar eritilerek nakit akışına kazandırılabilir.</div>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm font-black text-amber-950" id="execExcessStockCost">₺498.312</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 🏷️ TABLO 1: KATEGORİ BAZLI HEDEF YGS VS MEVCUT YGS KARŞILAŞTIRMASI -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-100">
                        <div>
                            <h3 class="font-black text-slate-900 text-sm flex items-center gap-2">
                                <i class="fa-solid fa-hourglass-half text-amber-600"></i> Kategori Bazlı Hedef YGS vs Mevcut Durum YGS Karşılaştırması
                            </h3>
                            <p class="text-[10px] text-slate-500">Her kategorinin devir hızı, hedef gün süresi ve kilitlenen fazla stok maliyetleri.</p>
                        </div>
                        <span class="text-[10px] font-bold text-slate-400">Referans İdeal YGS: 14 Gün</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold text-[10px] uppercase border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Kategori Adı</th>
                                    <th class="p-3 text-right">Bağlı Stok (TL)</th>
                                    <th class="p-3 text-center">Hedef YGS</th>
                                    <th class="p-3 text-center">Mevcut YGS</th>
                                    <th class="p-3 text-center">YGS Sapması</th>
                                    <th class="p-3 text-right">Bağlı Fazla Sermaye</th>
                                    <th class="p-3 text-center">Stok Durumu</th>
                                    <th class="p-3 text-center">Yönetici Aksiyonu</th>
                                </tr>
                            </thead>
                            <tbody id="execYgsCategoryTableBody" class="divide-y divide-slate-100 text-[11px]">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 🌟 3 BOYUTLU GMROI MASASI (SEKMELİ: SATINALMACI, KATEGORİ, ÜRETİCİ) -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-100">
                        <div>
                            <h3 class="font-black text-slate-900 text-sm flex items-center gap-2">
                                <i class="fa-solid fa-gem text-purple-600"></i> 3 Boyutlu GMROI (Stok Brüt Kâr Getirisi) Analizi
                            </h3>
                            <p class="text-[10px] text-slate-500">Bağlanan 1 TL stok sermayesinin ürettiği Brüt Kâr katsayısı (GMROI = Brüt Kâr / Ortalama Stok)</p>
                        </div>
                        <!-- Sekme Butonları -->
                        <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold">
                            <button onclick="setGmroiTab('BUYER')" id="btnGmroi_BUYER" class="px-3 py-1.5 rounded-lg bg-slate-900 text-white shadow-xs transition-all cursor-pointer">
                                👔 Satın Almacı Bazında
                            </button>
                            <button onclick="setGmroiTab('CATEGORY')" id="btnGmroi_CATEGORY" class="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all cursor-pointer">
                                🏷️ Kategori Bazında
                            </button>
                            <button onclick="setGmroiTab('SUPPLIER')" id="btnGmroi_SUPPLIER" class="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all cursor-pointer">
                                🏭 Üretici Firma Bazında
                            </button>
                        </div>
                    </div>

                    <!-- GMROI Tablo Alanı -->
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold text-[10px] uppercase border-b border-slate-200">
                                <tr id="execGmroiTableHeader">
                                    <th class="p-3">Adı / Tanımı</th>
                                    <th class="p-3 text-right">Satış Cirosu (TL)</th>
                                    <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                                    <th class="p-3 text-center">Kâr Marjı %</th>
                                    <th class="p-3 text-right font-bold text-slate-900">Bağlı Stok Maliyeti</th>
                                    <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI Oranı</th>
                                    <th class="p-3 text-center">Performans Değerlendirmesi</th>
                                </tr>
                            </thead>
                            <tbody id="execGmroiTableBody" class="divide-y divide-slate-100 text-[11px]">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 📐 SPACE-TO-SALES: KATEGORİ METREKARE VERİMLİLİĞİ VE ALAN TAHSİSİ -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-100">
                        <div>
                            <h3 class="font-black text-slate-900 text-sm flex items-center gap-2">
                                <i class="fa-solid fa-ruler-combined text-teal-600"></i> Kategori Metrekare Verimliliği & Alan Tahsis Analizi (Space-to-Sales)
                            </h3>
                            <p class="text-[10px] text-slate-500">Reyon m² Alan Payı (%) ile Ciro Payı (%) karşılaştırması ve alan genişletme/daraltma önerileri.</p>
                        </div>
                        <span class="text-[10px] font-bold text-slate-400">Toplam Satış Alanı: 2.450 m²</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold text-[10px] uppercase border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Reyon / Kategori</th>
                                    <th class="p-3 text-center">Tahsis Alan (m²)</th>
                                    <th class="p-3 text-center">Alan Payı %</th>
                                    <th class="p-3 text-right font-bold text-slate-900">3 Aylık Ciro (TL)</th>
                                    <th class="p-3 text-center font-bold text-blue-700">Ciro Payı %</th>
                                    <th class="p-3 text-right font-black text-teal-700">m² Verimi (TL/m²)</th>
                                    <th class="p-3 text-center bg-teal-50 text-teal-950 font-black">Alan İndeksi</th>
                                    <th class="p-3 text-center">Stratejik Alan Kararı</th>
                                </tr>
                            </thead>
                            <tbody id="execSpaceToSalesTableBody" class="divide-y divide-slate-100 text-[11px]">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 🤖 AI STRATEJİK PATRON KARAR DESTEK VE ERKEN UYARI MASASI -->
                <div class="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6 rounded-3xl shadow-lg border border-indigo-900/50 text-white space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-indigo-900/50">
                        <div class="flex items-center gap-2.5">
                            <div class="w-9 h-9 rounded-xl bg-amber-400 text-slate-950 flex items-center justify-center font-black text-lg shadow-md">
                                <i class="fa-solid fa-brain"></i>
                            </div>
                            <div>
                                <h3 class="font-black text-white text-base">AI Stratejik Patron Karar Destek Masası</h3>
                                <p class="text-xs text-indigo-200/80">Algoritmik anomali tespiti ve yönetici aksiyon önerileri</p>
                            </div>
                        </div>
                        <span class="bg-indigo-500/30 text-indigo-200 border border-indigo-400/40 text-[10px] font-bold px-3 py-1 rounded-full">4 Kritik İçgörü</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="execAiInsightsContainer">
                        <!-- Populated dynamically via JS -->
                    </div>
                </div>

                <!-- Büyüme & Kırılım Tabloları (Şubeler, Tedarikçiler, Satınalmacılar) -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
                    <div class="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-slate-100">
                        <div>
                            <h3 class="font-black text-slate-900 text-sm flex items-center gap-2">
                                <i class="fa-solid fa-chart-bar text-blue-600"></i> Şube, Kategori ve Üretici Büyüme Matrisi
                            </h3>
                            <p class="text-[10px] text-slate-500">Konsolide Ciro, Kâr ve Stok Yükü Kırılımları</p>
                        </div>
                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="setExecutivePerspective('STORES')" id="btnExecPersp_STORES" class="exec-persp-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-900 text-white shadow-xs cursor-pointer">
                                🏪 Şubeler Bazında
                            </button>
                            <button onclick="setExecutivePerspective('SUPPLIERS')" id="btnExecPersp_SUPPLIERS" class="exec-persp-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer">
                                🏭 Üreticiler Bazında
                            </button>
                            <button onclick="setExecutivePerspective('BUYERS')" id="btnExecPersp_BUYERS" class="exec-persp-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer">
                                👔 Satın Almacılar Bazında
                            </button>
                        </div>
                    </div>

                    <!-- Perspective 1: Stores Breakdown -->
                    <div id="execPersp_STORES" class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold text-[10px] uppercase border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Mağaza / Şube Adı</th>
                                    <th class="p-3 text-right font-bold text-slate-900">3 Aylık Ciro (TL)</th>
                                    <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                                    <th class="p-3 text-center font-bold text-emerald-800">Kâr Marjı %</th>
                                    <th class="p-3 text-right font-bold text-purple-950">Stok Sermayesi</th>
                                    <th class="p-3 text-center">YGS (Gün)</th>
                                    <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI</th>
                                    <th class="p-3 text-center text-rose-600 font-bold">Kritik Stok</th>
                                </tr>
                            </thead>
                            <tbody id="execStoreTableBody" class="divide-y divide-slate-100 text-[11px]">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Perspective 2: Suppliers Breakdown -->
                    <div id="execPersp_SUPPLIERS" class="hidden overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold text-[10px] uppercase border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Üretici / Tedarikçi Firma</th>
                                    <th class="p-3 text-right font-bold text-slate-900">Satış Cirosu (TL)</th>
                                    <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                                    <th class="p-3 text-center font-bold text-emerald-800">Kâr Marjı %</th>
                                    <th class="p-3 text-right font-bold text-purple-950">Bağlı Stok</th>
                                    <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI</th>
                                    <th class="p-3 text-center">BCG Matrisi</th>
                                    <th class="p-3 text-center">Vade Açığı</th>
                                </tr>
                            </thead>
                            <tbody id="execSupplierTableBody" class="divide-y divide-slate-100 text-[11px]">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Perspective 3: Buyers Breakdown -->
                    <div id="execPersp_BUYERS" class="hidden overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold text-[10px] uppercase border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Satın Alma Müdürü</th>
                                    <th class="p-3">Sorumluluk Alanı</th>
                                    <th class="p-3 text-right font-bold text-slate-900">3 Aylık Ciro (TL)</th>
                                    <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                                    <th class="p-3 text-center font-bold text-emerald-800">Kâr Marjı %</th>
                                    <th class="p-3 text-right font-bold text-purple-950">Stok Sermayesi</th>
                                    <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI</th>
                                    <th class="p-3 text-center">Performans</th>
                                </tr>
                            </thead>
                            <tbody id="execBuyerTableBody" class="divide-y divide-slate-100 text-[11px]">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

            </section>
"""

    # Replace section-executive in html
    pat = re.compile(r'<!-- SECTION 0: EXECUTIVE \(PATRON.*?-->.*?<!-- SECTION 1: PURCHASING WORKBENCH -->', re.DOTALL)
    if not pat.search(html):
        pat = re.compile(r'<section id="section-executive".*?<!-- SECTION 1: PURCHASING WORKBENCH -->', re.DOTALL)

    html = pat.sub(exec_html + '\n            <!-- SECTION 1: PURCHASING WORKBENCH -->', html, count=1)

    # 2. Append/update JavaScript rendering functions for Patron Cockpit
    js_code = """
        // =========================================================================
        // 👑 PATRON & GENEL MÜDÜR KOKPİTİ RENDER VE EXPORT MOTORU
        // =========================================================================
        let currentGmroiTab = 'BUYER';

        function setGmroiTab(tab) {
            currentGmroiTab = tab;
            ['BUYER', 'CATEGORY', 'SUPPLIER'].forEach(t => {
                const btn = document.getElementById(`btnGmroi_${t}`);
                if (btn) {
                    if (t === tab) {
                        btn.className = 'px-3 py-1.5 rounded-lg bg-slate-900 text-white shadow-xs transition-all cursor-pointer';
                    } else {
                        btn.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition-all cursor-pointer';
                    }
                }
            });

            if (window.executiveRawData) {
                renderGmroiTable(window.executiveRawData);
            }
        }

        function renderGmroiTable(d) {
            const tbody = document.getElementById('execGmroiTableBody');
            const theadTr = document.getElementById('execGmroiTableHeader');
            if (!tbody) return;

            if (currentGmroiTab === 'BUYER') {
                if (theadTr) {
                    theadTr.innerHTML = `
                        <th class="p-3">Satın Alma Müdürü</th>
                        <th class="p-3 text-right">3 Aylık Ciro (TL)</th>
                        <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                        <th class="p-3 text-center">Kâr Marjı %</th>
                        <th class="p-3 text-right font-bold text-slate-900">Bağlı Stok Maliyeti</th>
                        <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI Oranı</th>
                        <th class="p-3 text-center">Performans Değerlendirmesi</th>
                    `;
                }
                const list = d.gmroi_by_buyer || [];
                tbody.innerHTML = list.map(b => `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-bold text-slate-900 flex items-center gap-2">
                            <i class="fa-solid fa-user-tie text-blue-600"></i> ${b.buyer_name}
                        </td>
                        <td class="p-3 text-right font-semibold text-slate-700">₺${b.revenue.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-right font-bold text-emerald-700">₺${b.profit.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-center font-bold text-emerald-800">%${b.margin_pct.toFixed(1)}</td>
                        <td class="p-3 text-right font-bold text-slate-900">₺${b.stock_cost.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-center bg-purple-50 font-black text-purple-950 text-xs">${b.gmroi.toFixed(2)}x</td>
                        <td class="p-3 text-center">
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${
                                b.performance_badge === 'YÜKSEK' ? 'bg-emerald-100 text-emerald-800' :
                                b.performance_badge === 'ORTA' ? 'bg-blue-100 text-blue-800' : 'bg-rose-100 text-rose-800'
                            }">${b.performance_badge} PERFORMANS</span>
                        </td>
                    </tr>
                `).join('');
            } else if (currentGmroiTab === 'CATEGORY') {
                if (theadTr) {
                    theadTr.innerHTML = `
                        <th class="p-3">Kategori Adı</th>
                        <th class="p-3 text-right">3 Aylık Ciro (TL)</th>
                        <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                        <th class="p-3 text-center">Kâr Marjı %</th>
                        <th class="p-3 text-right font-bold text-slate-900">Bağlı Stok Maliyeti</th>
                        <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI Oranı</th>
                        <th class="p-3 text-center">Sermaye Sağlığı</th>
                    `;
                }
                const list = d.gmroi_by_category || [];
                tbody.innerHTML = list.map(c => `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-bold text-slate-900 flex items-center gap-2">
                            <i class="fa-solid fa-layer-group text-purple-600"></i> ${c.category_name}
                        </td>
                        <td class="p-3 text-right font-semibold text-slate-700">₺${c.revenue.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-right font-bold text-emerald-700">₺${c.profit.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-center font-bold text-emerald-800">%${c.margin_pct.toFixed(1)}</td>
                        <td class="p-3 text-right font-bold text-slate-900">₺${c.stock_cost.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-center bg-purple-50 font-black text-purple-950 text-xs">${c.gmroi.toFixed(2)}x</td>
                        <td class="p-3 text-center">
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${
                                c.performance_badge === 'YILDIZ' ? 'bg-emerald-100 text-emerald-800' :
                                c.performance_badge === 'SAĞLIKLI' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                            }">${c.performance_badge === 'YILDIZ' ? '🌟 YILDIZ KÂR MOTORU' : (c.performance_badge === 'SAĞLIKLI' ? '✅ SAĞLIKLI' : '⚠️ SERMAYE YÜKÜ')}</span>
                        </td>
                    </tr>
                `).join('');
            } else if (currentGmroiTab === 'SUPPLIER') {
                if (theadTr) {
                    theadTr.innerHTML = `
                        <th class="p-3">Üretici / Tedarikçi Firma</th>
                        <th class="p-3 text-right">3 Aylık Ciro (TL)</th>
                        <th class="p-3 text-right font-bold text-emerald-700">Brüt Kâr (TL)</th>
                        <th class="p-3 text-center">Kâr Marjı %</th>
                        <th class="p-3 text-right font-bold text-slate-900">Bağlı Stok</th>
                        <th class="p-3 text-center bg-purple-50 text-purple-950 font-black">GMROI</th>
                        <th class="p-3 text-center">BCG Segmenti</th>
                    `;
                }
                const list = d.gmroi_by_supplier || [];
                tbody.innerHTML = list.map(s => `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-bold text-slate-900 flex items-center gap-2">
                            <i class="fa-solid fa-industry text-indigo-600"></i> ${s.supplier_name}
                        </td>
                        <td class="p-3 text-right font-semibold text-slate-700">₺${s.revenue.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-right font-bold text-emerald-700">₺${s.profit.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-center font-bold text-emerald-800">%${s.margin_pct.toFixed(1)}</td>
                        <td class="p-3 text-right font-bold text-slate-900">₺${s.stock_cost.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                        <td class="p-3 text-center bg-purple-50 font-black text-purple-950 text-xs">${s.gmroi.toFixed(2)}x</td>
                        <td class="p-3 text-center">
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${
                                s.bcg_segment === 'YILDIZ' ? 'bg-emerald-100 text-emerald-800' :
                                s.bcg_segment === 'NAKİT İNEĞİ' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                            }">${s.bcg_segment}</span>
                        </td>
                    </tr>
                `).join('');
            }
        }

        function renderYgsCategoryTable(list) {
            const tbody = document.getElementById('execYgsCategoryTableBody');
            if (!tbody) return;
            if (!list || list.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="p-4 text-center text-slate-400">YGS verisi bulunamadı.</td></tr>`;
                return;
            }

            tbody.innerHTML = list.map(item => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-3 font-bold text-slate-900">${item.category_name}</td>
                    <td class="p-3 text-right font-semibold text-slate-700">₺${item.stock_cost.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                    <td class="p-3 text-center font-bold text-slate-600">${item.target_ygs.toFixed(0)} Gün</td>
                    <td class="p-3 text-center font-black ${item.current_ygs > item.target_ygs + 2 ? 'text-amber-700' : 'text-slate-900'}">${item.current_ygs.toFixed(1)} Gün</td>
                    <td class="p-3 text-center font-bold ${item.ygs_diff > 2 ? 'text-rose-600' : 'text-emerald-600'}">
                        ${item.ygs_diff > 0 ? '+' : ''}${item.ygs_diff.toFixed(1)}g
                    </td>
                    <td class="p-3 text-right font-black ${item.excess_stock_cost > 0 ? 'text-amber-900' : 'text-slate-400'}">
                        ${item.excess_stock_cost > 0 ? '₺' + item.excess_stock_cost.toLocaleString('tr-TR', {minimumFractionDigits: 0}) : '—'}
                    </td>
                    <td class="p-3 text-center">
                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            item.status === 'OPTIMUM' ? 'bg-emerald-100 text-emerald-800' :
                            item.status === 'FAZLA_STOK' ? 'bg-amber-100 text-amber-900' : 'bg-rose-100 text-rose-800'
                        }">
                            ${item.status === 'OPTIMUM' ? '✅ OPTİMUM' : (item.status === 'FAZLA_STOK' ? '⚠️ FAZLA STOK' : '🚨 KRİTİK DÜŞÜK')}
                        </span>
                    </td>
                    <td class="p-3 text-center">
                        ${item.status === 'FAZLA_STOK' ? 
                            '<button onclick=\"switchTab(\\'campaigns\\')\" class=\"bg-amber-100 hover:bg-amber-200 text-amber-900 px-2 py-1 rounded text-[10px] font-bold cursor-pointer\">⚡ Kampanya Aç</button>' :
                            (item.status === 'KRITIK_DUSUK' ? '<button onclick=\"switchTab(\\'workbench\\')\" class=\"bg-rose-600 hover:bg-rose-700 text-white px-2 py-1 rounded text-[10px] font-bold cursor-pointer\">🚀 İkmal Yap</button>' : '<span class=\"text-[10px] text-emerald-600 font-bold\">Dengeli</span>')
                        }
                    </td>
                </tr>
            `).join('');
        }

        function renderSpaceToSalesTable(list) {
            const tbody = document.getElementById('execSpaceToSalesTableBody');
            if (!tbody) return;
            if (!list || list.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="p-4 text-center text-slate-400">Space-to-Sales verisi bulunamadı.</td></tr>`;
                return;
            }

            tbody.innerHTML = list.map(item => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-3 font-bold text-slate-900">${item.category_name}</td>
                    <td class="p-3 text-center font-semibold text-slate-700">${item.allocated_sqm.toFixed(0)} m²</td>
                    <td class="p-3 text-center font-bold text-slate-600">%${item.sqm_share_pct.toFixed(1)}</td>
                    <td class="p-3 text-right font-bold text-slate-900">₺${item.revenue_3m.toLocaleString('tr-TR', {minimumFractionDigits: 0})}</td>
                    <td class="p-3 text-center font-bold text-blue-700">%${item.revenue_share_pct.toFixed(1)}</td>
                    <td class="p-3 text-right font-black text-teal-800">₺${item.revenue_per_sqm.toLocaleString('tr-TR', {minimumFractionDigits: 0})} / m²</td>
                    <td class="p-3 text-center bg-teal-50 font-black text-teal-950 text-xs">${item.space_productivity_index.toFixed(2)}x</td>
                    <td class="p-3 text-center">
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-black ${
                            item.recommendation === 'ALANI BÜYÜT' ? 'bg-emerald-100 text-emerald-800' :
                            item.recommendation === 'ALANI KORU' ? 'bg-blue-100 text-blue-800' : 'bg-rose-100 text-rose-800'
                        }">${item.recommendation}</span>
                    </td>
                </tr>
            `).join('');
        }

        function renderExecutiveAIInsights(list) {
            const container = document.getElementById('execAiInsightsContainer');
            if (!container) return;
            if (!list || list.length === 0) {
                container.innerHTML = `<div class="col-span-2 p-4 text-center text-indigo-300">Tüm göstergeler olağan seviyededir.</div>`;
                return;
            }

            container.innerHTML = list.map(item => `
                <div class="p-4 rounded-2xl ${
                    item.type === 'DANGER' ? 'bg-rose-950/60 border border-rose-500/40 text-rose-100' :
                    item.type === 'WARNING' ? 'bg-amber-950/60 border border-amber-500/40 text-amber-100' :
                    item.type === 'OPPORTUNITY' ? 'bg-teal-950/60 border border-teal-500/40 text-teal-100' :
                    'bg-emerald-950/60 border border-emerald-500/40 text-emerald-100'
                } space-y-2">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-black flex items-center gap-1.5 ${
                            item.type === 'DANGER' ? 'text-rose-400' :
                            item.type === 'WARNING' ? 'text-amber-400' :
                            item.type === 'OPPORTUNITY' ? 'text-teal-400' : 'text-emerald-400'
                        }">
                            <i class="fa-solid ${
                                item.type === 'DANGER' ? 'fa-triangle-exclamation' :
                                item.type === 'WARNING' ? 'fa-hourglass-half' :
                                item.type === 'OPPORTUNITY' ? 'fa-lightbulb' : 'fa-circle-check'
                            }"></i>
                            ${item.title}
                        </span>
                        <span class="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                            item.type === 'DANGER' ? 'bg-rose-900/60 text-rose-300' :
                            item.type === 'WARNING' ? 'bg-amber-900/60 text-amber-300' :
                            item.type === 'OPPORTUNITY' ? 'bg-teal-900/60 text-teal-300' : 'bg-emerald-900/60 text-emerald-300'
                        }">${item.type}</span>
                    </div>
                    <p class="text-[11px] text-slate-300 leading-relaxed">${item.description}</p>
                    <div class="pt-1 flex items-center justify-between">
                        <span class="text-[10px] text-indigo-300 font-semibold">Önerilen Yönetici Kararı:</span>
                        <span class="text-[10px] font-bold text-white bg-white/10 px-2 py-1 rounded-lg border border-white/10">${item.action_label}</span>
                    </div>
                </div>
            `).join('');
        }

        // PDF ve Excel Dışa Aktarma Motorları
        function exportPatronCockpitPDF() {
            if (!window.executiveRawData) {
                showToast("Yüklenecek patron verisi bulunamadı!", "warning");
                return;
            }
            const d = window.executiveRawData;
            const todayStr = '06.09.2026';
            const printWindow = window.open('', '_blank', 'width=1100,height=850');
            if (!printWindow) {
                alert('Lütfen açılır pencerelere izin veriniz.');
                return;
            }

            printWindow.document.write(`
                <!DOCTYPE html>
                <html lang="tr">
                <head>
                    <meta charset="UTF-8">
                    <title>MarketYönetimi360 - Patron & Genel Müdür Yönetim Raporu</title>
                    <style>
                        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 24px; color: #0f172a; }
                        .header-box { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 16px; }
                        .logo-text { font-size: 22px; font-weight: 900; color: #0f172a; }
                        .logo-tag { background: #2563eb; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-left: 4px; }
                        .grid-kpi { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
                        .kpi-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; }
                        .kpi-title { font-size: 10px; color: #64748b; font-weight: bold; text-transform: uppercase; }
                        .kpi-val { font-size: 18px; font-weight: 900; color: #0f172a; margin-top: 2px; }
                        .kpi-sub { font-size: 10px; color: #16a34a; font-weight: bold; margin-top: 2px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; font-size: 11px; }
                        th { background: #f1f5f9; color: #334155; padding: 8px; border-bottom: 2px solid #cbd5e1; text-align: left; }
                        td { padding: 6px 8px; border-bottom: 1px solid #e2e8f0; }
                        h3 { font-size: 14px; color: #1e3a8a; margin: 16px 0 6px 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
                        @media print { button { display: none !important; } }
                    </style>
                </head>
                <body>
                    <div style="text-align: right; margin-bottom: 10px;">
                        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer;">🖨️ Yazdır / PDF Kaydet</button>
                    </div>
                    <div class="header-box">
                        <div>
                            <div class="logo-text">MarketYönetimi<span class="logo-tag">360</span></div>
                            <h2 style="margin: 4px 0 0 0; font-size: 18px; color: #1e3a8a;">Patron, Genel Müdür & CEO — Konsolide Yönetim Raporu</h2>
                        </div>
                        <div style="text-align: right; font-size: 11px; color: #475569;">
                            <div><b>Rapor Tarihi:</b> ${todayStr}</div>
                            <div><b>Dönem:</b> 2026 vs 2025 Yıllık & Q3 Kıyaslaması</div>
                        </div>
                    </div>

                    <div class="grid-kpi">
                        <div class="kpi-card">
                            <div class="kpi-title">Satış Cirosu (Bu Yıl)</div>
                            <div class="kpi-val">₺${d.total_network_revenue.toLocaleString('tr-TR', {maximumFractionDigits:0})}</div>
                            <div class="kpi-sub">Nominal Büyüme: %+${d.revenue_growth_nominal_pct.toFixed(1)}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Gıda Enflasyonu vs Reel Büyüme</div>
                            <div class="kpi-val" style="color: #dc2626;">Reel: %${d.real_growth_pct.toFixed(1)}</div>
                            <div style="font-size:10px; color:#475569;">TÜİK Enflasyon: %${d.food_inflation_rate_pct} • Sektör: %${d.sector_growth_rate_pct}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Personel & m² Verimliliği</div>
                            <div class="kpi-val">₺${d.revenue_per_staff.toLocaleString('tr-TR', {maximumFractionDigits:0})} / Kişi</div>
                            <div style="font-size:10px; color:#475569;">m² Satış Verimi: ₺${d.revenue_per_sqm.toLocaleString('tr-TR', {maximumFractionDigits:0})} / m²</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Brüt Kârlılık</div>
                            <div class="kpi-val" style="color: #16a34a;">₺${d.total_network_profit.toLocaleString('tr-TR', {maximumFractionDigits:0})}</div>
                            <div style="font-size:10px; color:#16a34a;">Marj: %${d.network_margin_pct.toFixed(1)} (Hedef %28 Aşıldı)</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Stok YGS & Fazla Sermaye</div>
                            <div class="kpi-val" style="color: #d97706;">${d.avg_days_of_inventory.toFixed(1)} Gün</div>
                            <div style="font-size:10px; color:#d97706;">Fazla Stok: ₺${d.excess_inventory_cost.toLocaleString('tr-TR', {maximumFractionDigits:0})}</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Konsolide GMROI</div>
                            <div class="kpi-val" style="color: #7c3aed;">${d.overall_gmroi.toFixed(2)}x</div>
                            <div style="font-size:10px; color:#7c3aed;">₺1 Stok = ₺${d.overall_gmroi.toFixed(2)} Kâr</div>
                        </div>
                    </div>

                    <h3>1. Kategori Bazlı Hedef YGS vs Mevcut Durum YGS Karşılaştırması</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Kategori</th>
                                <th style="text-align:right;">Bağlı Stok (TL)</th>
                                <th style="text-align:center;">Hedef YGS</th>
                                <th style="text-align:center;">Mevcut YGS</th>
                                <th style="text-align:center;">YGS Sapması</th>
                                <th style="text-align:right;">Fazla Sermaye Yükü</th>
                                <th style="text-align:center;">Durum</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${(d.ygs_category_comparison || []).map(r => `
                                <tr>
                                    <td><b>${r.category_name}</b></td>
                                    <td style="text-align:right;">₺${r.stock_cost.toLocaleString('tr-TR', {maximumFractionDigits:0})}</td>
                                    <td style="text-align:center;">${r.target_ygs} Gün</td>
                                    <td style="text-align:center; font-weight:bold;">${r.current_ygs.toFixed(1)} Gün</td>
                                    <td style="text-align:center; color:${r.ygs_diff > 2 ? '#dc2626' : '#16a34a'}; font-weight:bold;">${r.ygs_diff > 0 ? '+' : ''}${r.ygs_diff.toFixed(1)}g</td>
                                    <td style="text-align:right; font-weight:bold;">${r.excess_stock_cost > 0 ? '₺' + r.excess_stock_cost.toLocaleString('tr-TR', {maximumFractionDigits:0}) : '—'}</td>
                                    <td style="text-align:center;">${r.status}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>

                    <h3>2. Space-to-Sales (Kategori Metrekare Verimliliği ve Alan Tahsisi)</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Reyon / Kategori</th>
                                <th style="text-align:center;">Tahsis Alan (m²)</th>
                                <th style="text-align:center;">Alan Payı %</th>
                                <th style="text-align:right;">Ciro (TL)</th>
                                <th style="text-align:center;">Ciro Payı %</th>
                                <th style="text-align:right;">m² Verimi (TL/m²)</th>
                                <th style="text-align:center;">Alan İndeksi</th>
                                <th style="text-align:center;">Stratejik Alan Kararı</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${(d.space_to_sales_categories || []).map(r => `
                                <tr>
                                    <td><b>${r.category_name}</b></td>
                                    <td style="text-align:center;">${r.allocated_sqm} m²</td>
                                    <td style="text-align:center;">%${r.sqm_share_pct}</td>
                                    <td style="text-align:right;">₺${r.revenue_3m.toLocaleString('tr-TR', {maximumFractionDigits:0})}</td>
                                    <td style="text-align:center;">%${r.revenue_share_pct}</td>
                                    <td style="text-align:right; font-weight:bold;">₺${r.revenue_per_sqm.toLocaleString('tr-TR', {maximumFractionDigits:0})}</td>
                                    <td style="text-align:center; font-weight:bold;">${r.space_productivity_index}x</td>
                                    <td style="text-align:center; font-weight:bold;">${r.recommendation}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </body>
                </html>
            `);
            printWindow.document.close();
            setTimeout(() => { printWindow.print(); }, 300);
            showToast("Patron Yönetim Raporu PDF formatında hazırlandı.", "success");
        }

        function exportPatronCockpitExcel() {
            if (!window.executiveRawData) {
                showToast("Yüklenecek patron verisi bulunamadı!", "warning");
                return;
            }
            const d = window.executiveRawData;
            const todayStr = '06.09.2026';

            const rowsHtml = (d.categories_performance || []).map((c, i) => `
                <tr>
                    <td>${i + 1}</td>
                    <td><b>${c.category_name}</b></td>
                    <td>₺${c.revenue_3m.toLocaleString('tr-TR')}</td>
                    <td>₺${c.profit_3m.toLocaleString('tr-TR')}</td>
                    <td>%${c.margin_pct.toFixed(1)}</td>
                    <td>₺${c.stock_cost.toLocaleString('tr-TR')}</td>
                    <td>${c.days_of_inventory.toFixed(1)} Gün</td>
                    <td>${c.gmroi_ratio.toFixed(2)}x</td>
                </tr>
            `).join('');

            const excelTemplate = `
                <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
                <head><meta charset="utf-8"></head>
                <body>
                    <table>
                        <tr><td colspan="8" style="font-size:16pt; font-weight:bold; color:#1e3a8a;">MarketYönetimi360 — Patron & CEO Yönetim Özeti</td></tr>
                        <tr><td colspan="8"><b>Rapor Tarihi:</b> ${todayStr} | <b>Toplam Ciro:</b> ₺${d.total_network_revenue.toLocaleString('tr-TR')} | <b>Nominal Büyüme:</b> %+${d.revenue_growth_nominal_pct}% | <b>Reel Büyüme:</b> %${d.real_growth_pct}%</td></tr>
                        <tr></tr>
                        <thead>
                            <tr style="background:#2563eb; color:#ffffff; font-weight:bold;">
                                <th>#</th>
                                <th>Kategori Adı</th>
                                <th>3 Aylık Ciro (TL)</th>
                                <th>Brüt Kâr (TL)</th>
                                <th>Kâr Marjı %</th>
                                <th>Bağlı Stok (TL)</th>
                                <th>Stok YGS (Gün)</th>
                                <th>GMROI</th>
                            </tr>
                        </thead>
                        <tbody>${rowsHtml}</tbody>
                    </table>
                </body>
                </html>
            `;

            const blob = new Blob(['\\ufeff' + excelTemplate], { type: 'application/vnd.ms-excel;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `Patron_Yonetim_Ozeti_${todayStr}.xls`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
            showToast("Patron Yönetim Özeti Excel formatında indirildi!", "success");
        }
    """

    # Check if renderGmroiTable exists, if not append before </script>
    if 'function setGmroiTab' not in html:
        html = html.replace('</script>', js_code + '\n    </script>')

    # Update loadExecutiveDashboard JS function to populate all new widgets
    load_exec_regex = re.compile(r'async function loadExecutiveDashboard\(\) \{.*?document\.getElementById\(\'execKpiRevenue\'\)\.innerText = `₺\$\{d\.total_network_revenue\.toLocaleString\(.*?\)\}`;', re.DOTALL)
    
    new_populate_block = """async function loadExecutiveDashboard() {
            const storeId = document.getElementById('execStoreFilter')?.value || '';
            const buyerId = document.getElementById('execBuyerFilter')?.value || '';
            const supId = document.getElementById('execSupplierFilter')?.value || '';
            const catId = document.getElementById('execCategoryFilter')?.value || '';
            const period = document.getElementById('execPeriodFilter')?.value || 'YOY_2026_2025';

            let query = '?';
            if (storeId) query += `store_id=${storeId}&`;
            if (buyerId) query += `buyer_id=${buyerId}&`;
            if (supId) query += `supplier_id=${supId}&`;
            if (catId) query += `category_id=${catId}&`;

            try {
                const res = await fetch(`${API_BASE}/analytics/executive-summary${query}`);
                if (!res.ok) throw new Error("Executive API error");
                executiveRawData = await res.json();
                window.executiveRawData = executiveRawData;
                const d = executiveRawData;

                // 1. Populate Master KPI Cards
                if (document.getElementById('execKpiRevenue')) {
                    document.getElementById('execKpiRevenue').innerText = `₺${d.total_network_revenue.toLocaleString('tr-TR', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
                }
                if (document.getElementById('execKpiRevenueGrowth')) {
                    document.getElementById('execKpiRevenueGrowth').innerText = `%+${d.revenue_growth_nominal_pct.toFixed(1)} Büyüme`;
                }
                if (document.getElementById('execKpiPriorRevenue')) {
                    document.getElementById('execKpiPriorRevenue').innerText = `Geçen Yıl: ₺${d.prior_year_revenue.toLocaleString('tr-TR', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
                }
                if (document.getElementById('execKpiQty')) {
                    document.getElementById('execKpiQty').innerText = `${Math.round(d.current_year_qty).toLocaleString('tr-TR')} Adet`;
                }
                if (document.getElementById('execKpiQtyGrowth')) {
                    document.getElementById('execKpiQtyGrowth').innerText = `%+${d.qty_growth_pct.toFixed(1)} Hacim Artışı`;
                }
                if (document.getElementById('execKpiPriorQty')) {
                    document.getElementById('execKpiPriorQty').innerText = `Geçen Yıl: ${Math.round(d.prior_year_qty).toLocaleString('tr-TR')} Adet`;
                }
                if (document.getElementById('execKpiRealGrowth')) {
                    document.getElementById('execKpiRealGrowth').innerText = `%${d.real_growth_pct.toFixed(1)}`;
                }
                if (document.getElementById('execKpiMarketShare')) {
                    document.getElementById('execKpiMarketShare').innerText = `${d.market_share_diff_pct.toFixed(1)} Puan`;
                }
                if (document.getElementById('execKpiStaffProd')) {
                    document.getElementById('execKpiStaffProd').innerText = `₺${d.revenue_per_staff.toLocaleString('tr-TR', {maximumFractionDigits: 0})} / Kişi`;
                }
                if (document.getElementById('execKpiSqmProd')) {
                    document.getElementById('execKpiSqmProd').innerText = `m² Verimi: ₺${d.revenue_per_sqm.toLocaleString('tr-TR', {maximumFractionDigits: 0})} / m²`;
                }
                if (document.getElementById('execKpiBasketAvg')) {
                    document.getElementById('execKpiBasketAvg').innerText = `₺${d.avg_basket_amount.toFixed(2)}`;
                }
                if (document.getElementById('execKpiCustomerCount')) {
                    document.getElementById('execKpiCustomerCount').innerText = `${d.total_customer_count.toLocaleString('tr-TR')} Fiş • 5.2 Parça`;
                }
                if (document.getElementById('execKpiPriorBasket')) {
                    document.getElementById('execKpiPriorBasket').innerText = `Geçen Yıl: ₺${d.prior_avg_basket_amount.toFixed(2)}`;
                }

                // 2. Populate Profit & Stock Panels
                if (document.getElementById('execTargetProfitTry')) {
                    document.getElementById('execTargetProfitTry').innerText = `Hedef: ₺${d.target_gross_profit.toLocaleString('tr-TR', {maximumFractionDigits: 0})}`;
                }
                if (document.getElementById('execActualMargin')) {
                    document.getElementById('execActualMargin').innerText = `%${d.network_margin_pct.toFixed(1)}`;
                }
                if (document.getElementById('execActualProfitVal')) {
                    document.getElementById('execActualProfitVal').innerText = `₺${d.total_network_profit.toLocaleString('tr-TR', {maximumFractionDigits: 0})}`;
                }
                if (document.getElementById('execProfitVariancePct')) {
                    document.getElementById('execProfitVariancePct').innerText = `+₺${d.gross_profit_variance_try.toLocaleString('tr-TR', {maximumFractionDigits: 0})}`;
                }
                if (document.getElementById('execProfitVarianceTry')) {
                    document.getElementById('execProfitVarianceTry').innerText = `+₺${d.gross_profit_variance_try.toLocaleString('tr-TR', {maximumFractionDigits: 0})}`;
                }
                if (document.getElementById('execActualYgs')) {
                    document.getElementById('execActualYgs').innerText = `${d.avg_days_of_inventory.toFixed(1)} Gün`;
                }
                if (document.getElementById('execActualStockCostVal')) {
                    document.getElementById('execActualStockCostVal').innerText = `₺${d.total_inventory_cost.toLocaleString('tr-TR', {maximumFractionDigits: 0})} Stok`;
                }
                if (document.getElementById('execActualGmroiVal')) {
                    document.getElementById('execActualGmroiVal').innerText = `${d.overall_gmroi.toFixed(2)}x`;
                }
                if (document.getElementById('execExcessStockCost')) {
                    document.getElementById('execExcessStockCost').innerText = `₺${d.excess_inventory_cost.toLocaleString('tr-TR', {maximumFractionDigits: 0})}`;
                }

                // 3. Render Special Executive Tables
                renderYgsCategoryTable(d.ygs_category_comparison || []);
                renderGmroiTable(d);
                renderSpaceToSalesTable(d.space_to_sales_categories || []);
                renderExecutiveAIInsights(d.executive_ai_insights || []);"""

    html = load_exec_regex.sub(new_populate_block, html, count=1)

    with open('app/templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("dashboard.html updated successfully with complete Patron Cockpit UI & JS!")

if __name__ == '__main__':
    update_patron_cockpit()

