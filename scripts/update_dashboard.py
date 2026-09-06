# -*- coding: utf-8 -*-
"""
MarketYonetimi360 Dashboard Updater
Transforms dashboard.html into 11 main menus, meeting tabs, universal action-decision engine,
read-only consolidated summary, and integrated pages.
"""
import os
import re

SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# =========================================================================
# 1. NEW SIDEBAR HTML (11 MAIN MENUS)
# =========================================================================
new_sidebar_menu = """        <!-- 3 KADEMELİ HİYERARŞİK AKORDEON MENÜ: ANA MENÜ -> ALT MENÜ -> 2. ALT MENÜ -->
        <div class="p-3 space-y-2 flex-1 overflow-y-auto custom-scrollbar" id="sidebarMenu">

            <!-- ========================================== -->
            <!-- 1. ANA MENÜ: YÖNETİM ÖZETİ -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_mgmt')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_mgmt">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs group-hover:bg-blue-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-table-cells"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Yönetim Özeti</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_mgmt"></i>
                </button>
                
                <!-- 1. Alt Menüler (L2) -->
                <div id="sub-l1_mgmt" class="pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-blue-500/40">
                    
                    <!-- 1.1 Yönetim Özeti -->
                    <div>
                        <button onclick="toggleL2('l2_mgmt_summary', 'executive')" class="l2-btn active w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_mgmt_summary">
                            <div class="flex items-center gap-2.5">
                                <i class="fa-solid fa-table-cells text-xs text-blue-400 w-4 text-center"></i>
                                <span>Yönetim Özeti</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_mgmt_summary"></i>
                        </button>
                        <div id="sub-l2_mgmt_summary" class="pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'executive')" class="l3-btn active w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Konsolide Patron Kokpiti</button>
                            <button onclick="selectL3(this, 'executive'); openPatronDetailModal('all')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şube P&L Kâr/Zarar</button>
                            <button onclick="selectL3(this, 'executive')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Günlük Satış & Marj</button>
                            <button onclick="selectL3(this, 'meetings-summary')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-amber-300 hover:text-amber-200 hover:bg-white/5 transition-colors block font-bold">🆕 • Toplantılar Karar Özeti</button>
                        </div>
                    </div>

                    <!-- 1.2 Strateji ve Bütçe -->
                    <div>
                        <button onclick="toggleL2('l2_strategy', 'executive')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_strategy">
                            <div class="flex items-center gap-2.5">
                                <i class="fa-solid fa-chart-simple text-xs text-indigo-400 w-4 text-center"></i>
                                <span>Strateji ve Bütçe</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_strategy"></i>
                        </button>
                        <div id="sub-l2_strategy" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'executive')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Yıllık Stratejik Bütçe</button>
                            <button onclick="selectL3(this, 'executive')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Bütçe vs Gerçekleşen</button>
                            <button onclick="selectL3(this, 'burden')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• İşletme Sermayesi & DIO</button>
                        </div>
                    </div>

                    <!-- 1.3 Hedefler ve KPI’lar -->
                    <div>
                        <button onclick="toggleL2('l2_kpis', 'macro')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_kpis">
                            <div class="flex items-center gap-2.5">
                                <i class="fa-solid fa-circle-dot text-xs text-cyan-400 w-4 text-center"></i>
                                <span>Hedefler ve KPI’lar</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_kpis"></i>
                        </button>
                        <div id="sub-l2_kpis" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'macro')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şirket Skor Kartı (BSC)</button>
                            <button onclick="selectL3(this, 'executive')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şube Hedef Matrisi</button>
                            <button onclick="selectL3(this, 'macro')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• PerakendeData Kıyaslama</button>
                        </div>
                    </div>

                    <!-- 1.4 Görev ve Aksiyonlar -->
                    <div>
                        <button onclick="toggleL2('l2_actions', 'actions')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_actions">
                            <div class="flex items-center gap-2.5">
                                <i class="fa-solid fa-clipboard-check text-xs text-amber-400 w-4 text-center"></i>
                                <span>Görev ve Aksiyonlar</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="bg-amber-500 text-slate-950 text-[9px] font-black w-4 h-4 rounded-full flex items-center justify-center shadow-xs" id="actionCardsBadge">2</span>
                                <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_actions"></i>
                            </div>
                        </button>
                        <div id="sub-l2_actions" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'actions')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Açık Aksiyon Kartları</button>
                            <button onclick="selectL3(this, 'actions'); runComprehensiveAudit()" class="l3-btn w-full text-left py-1 px-2 rounded-md text-amber-300 hover:text-amber-200 hover:bg-white/5 transition-colors block font-medium">• Anomali Taraması Başlat</button>
                            <button onclick="selectL3(this, 'actions-resolved')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Çözülen Görevler & Tasarruf</button>
                        </div>
                    </div>

                    <!-- 1.5 Yönetim Toplantıları (YENİDEN YAPILANDIRILDI) -->
                    <div>
                        <button onclick="toggleL2('l2_meetings', 'meetings-icra')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_meetings">
                            <div class="flex items-center gap-2.5">
                                <i class="fa-solid fa-handshake text-xs text-purple-400 w-4 text-center"></i>
                                <span>Yönetim Toplantıları</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_meetings"></i>
                        </button>
                        <div id="sub-l2_meetings" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'meetings-icra')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • İcra Kurulu Toplantısı</button>
                            <button onclick="selectL3(this, 'meetings-purchasing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Satınalma & Kategori Toplantıları</button>
                            <button onclick="selectL3(this, 'meetings-field')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Saha & Satış Değerlendirme</button>
                            <button onclick="selectL3(this, 'meetings-tracking')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Toplantı Karar Takibi</button>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ========================================== -->
            <!-- 2. ANA MENÜ: TİCARİ YÖNETİM -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_commercial')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_commercial">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-cart-shopping"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Ticari Yönetim</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_commercial"></i>
                </button>

                <!-- 2. Alt Menüler (L2) -->
                <div id="sub-l1_commercial" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-emerald-500/40">
                    
                    <!-- 2.1 Satın Alma -->
                    <div>
                        <button onclick="toggleL2('l2_purchasing', 'workbench')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_purchasing">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-basket-shopping text-xs text-blue-400 w-4 text-center"></i>
                                <span>Satın Alma</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_purchasing"></i>
                        </button>
                        <div id="sub-l2_purchasing" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'workbench')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Satın Alma & Sipariş Tezgâhı</button>
                            <button onclick="selectL3(this, 'orders')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Verilen Siparişler & Vade</button>
                            <button onclick="selectL3(this, 'po-approvals')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Otomatik PO Onayları</button>
                        </div>
                    </div>

                    <!-- 2.2 Kategori ve Ürün -->
                    <div>
                        <button onclick="toggleL2('l2_category', 'category')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_category">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-cubes-stacked text-xs text-purple-400 w-4 text-center"></i>
                                <span>Kategori ve Ürün</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_category"></i>
                        </button>
                        <div id="sub-l2_category" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'category')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Kategori Ağacı & Rolleri</button>
                            <button onclick="selectL3(this, 'category')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• SKU Verimliliği (ABC/XYZ)</button>
                            <button onclick="selectL3(this, 'category')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Private Label (Özmarka) Payı</button>
                        </div>
                    </div>

                    <!-- 2.3 Tedarikçi Yönetimi -->
                    <div>
                        <button onclick="toggleL2('l2_suppliers', 'suppliers')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_suppliers">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-industry text-xs text-indigo-400 w-4 text-center"></i>
                                <span>Tedarikçi Yönetimi</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_suppliers"></i>
                        </button>
                        <div id="sub-l2_suppliers" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'suppliers')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Tedarikçi Karnesi & Skor</button>
                            <button onclick="selectL3(this, 'suppliers')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• BCG Matrisi (Ciro/Kâr)</button>
                            <button onclick="selectL3(this, 'contracts')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Dönem Sonu Ciro Primleri</button>
                        </div>
                    </div>

                    <!-- 2.4 Fiyat Yönetimi -->
                    <div>
                        <button onclick="toggleL2('l2_pricing', 'pricing')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_pricing">
                            <div class="flex items-center gap-2">
                                <i class="fa-regular fa-envelope-open text-xs text-emerald-400 w-4 text-center"></i>
                                <span>Fiyat Yönetimi</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_pricing"></i>
                        </button>
                        <div id="sub-l2_pricing" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'pricing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• KVI Fiyat İmajı & Rakip</button>
                            <button onclick="selectL3(this, 'pricing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Maliyet Artışı Fiyat Onayı</button>
                            <button onclick="selectL3(this, 'pricing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Kasa - Raf Fiyat Uyumu</button>
                        </div>
                    </div>

                    <!-- 2.5 Kampanyalar -->
                    <div>
                        <button onclick="toggleL2('l2_campaigns', 'campaigns')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_campaigns">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-bolt-lightning text-xs text-pink-400 w-4 text-center"></i>
                                <span>Kampanyalar</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_campaigns"></i>
                        </button>
                        <div id="sub-l2_campaigns" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'campaigns')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Kampanya Takvimi & ROI</button>
                            <button onclick="selectL3(this, 'campaigns')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• İnsert Ürün Analitiği</button>
                            <button onclick="selectL3(this, 'crm')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-rose-300 hover:text-rose-200 hover:bg-white/5 transition-colors block font-medium">• XPlusCRM Müşteri Teklifi</button>
                        </div>
                    </div>

                    <!-- 2.6 Pazarlama & Marka İletişimi (YENİ EKLENDİ) -->
                    <div>
                        <button onclick="toggleL2('l2_marketing', 'marketing')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_marketing">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-bullhorn text-xs text-amber-400 w-4 text-center"></i>
                                <span>Pazarlama & Marka</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_marketing"></i>
                        </button>
                        <div id="sub-l2_marketing" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'marketing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Yerel Pazarlama & Sosyal Medya</button>
                            <button onclick="selectL3(this, 'marketing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Şube Görsel Marka Standartları</button>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ========================================== -->
            <!-- 3. ANA MENÜ: TEDARİK ZİNCİRİ -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_supply')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_supply">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center text-xs group-hover:bg-teal-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-truck-ramp-box"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Tedarik Zinciri</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_supply"></i>
                </button>

                <!-- 3. Alt Menüler (L2) -->
                <div id="sub-l1_supply" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-teal-500/40">
                    
                    <!-- 3.1 Talep ve Tahmin -->
                    <div>
                        <button onclick="toggleL2('l2_demand', 'demand')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_demand">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-chart-line text-xs text-teal-400 w-4 text-center"></i>
                                <span>Talep ve Tahmin</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_demand"></i>
                        </button>
                        <div id="sub-l2_demand" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'demand')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• 3 Ay Geçmiş + 3 Ay Tahmin</button>
                            <button onclick="selectL3(this, 'demand')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Tahmin Doğruluk Oranı (WAPE)</button>
                        </div>
                    </div>

                    <!-- 3.2 Stok ve İkmal -->
                    <div>
                        <button onclick="toggleL2('l2_replenishment', 'stockouts')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_replenishment">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-boxes-stacked text-xs text-emerald-400 w-4 text-center"></i>
                                <span>Stok ve İkmal</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_replenishment"></i>
                        </button>
                        <div id="sub-l2_replenishment" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'stockouts')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-rose-300 hover:text-rose-200 hover:bg-white/5 transition-colors block font-medium">• Depoda Var Mağazada Yok</button>
                            <button onclick="selectL3(this, 'demand')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Güvenlik Stoğu & Min-Max</button>
                            <button onclick="selectL3(this, 'stores')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şubeler Arası Transfer</button>
                        </div>
                    </div>

                    <!-- 3.3 Depo Yönetimi -->
                    <div>
                        <button onclick="toggleL2('l2_warehouse', 'logistics')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_warehouse">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-warehouse text-xs text-sky-400 w-4 text-center"></i>
                                <span>Depo Yönetimi</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_warehouse"></i>
                        </button>
                        <div id="sub-l2_warehouse" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'logistics')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Merkez Depo Mal Kabul</button>
                            <button onclick="selectL3(this, 'logistics')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Depo Doluluk & Raf Düzeni</button>
                        </div>
                    </div>

                    <!-- 3.4 Lojistik ve Sevkiyat -->
                    <div>
                        <button onclick="toggleL2('l2_logistics', 'logistics')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_logistics">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-truck text-xs text-cyan-400 w-4 text-center"></i>
                                <span>Lojistik ve Sevkiyat</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_logistics"></i>
                        </button>
                        <div id="sub-l2_logistics" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'logistics')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şube Sevk Planı & Rota</button>
                            <button onclick="selectL3(this, 'logistics')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Araç Doluluk & Soğuk Zincir</button>
                            <button onclick="selectL3(this, 'logistics')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Koli Başı Lojistik Maliyet</button>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ========================================== -->
            <!-- 4. ANA MENÜ: MAĞAZA YÖNETİMİ -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_store')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_store">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs group-hover:bg-cyan-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-shop"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Mağaza Yönetimi</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_store"></i>
                </button>

                <!-- 4. Alt Menüler (L2) -->
                <div id="sub-l1_store" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-cyan-500/40">
                    
                    <!-- 4.1 Mağaza Operasyonları -->
                    <div>
                        <button onclick="toggleL2('l2_store_ops', 'stores')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_store_ops">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-store text-xs text-cyan-400 w-4 text-center"></i>
                                <span>Mağaza Operasyonları</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_store_ops"></i>
                        </button>
                        <div id="sub-l2_store_ops" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'stores')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Günlük Açılış/Kapanış Checklist</button>
                            <button onclick="selectL3(this, 'stores')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Kasa Tarama Hızı (IPM)</button>
                            <button onclick="selectL3(this, 'stores')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Mağaza Stok Sağlığı</button>
                        </div>
                    </div>

                    <!-- 4.2 Mağaza Karneleri -->
                    <div>
                        <button onclick="toggleL2('l2_store_scorecards', 'stores')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_store_scorecards">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-award text-xs text-amber-400 w-4 text-center"></i>
                                <span>Mağaza Karneleri</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_store_scorecards"></i>
                        </button>
                        <div id="sub-l2_store_scorecards" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'stores')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şube Satış & Kârlılık Puanı</button>
                            <button onclick="selectL3(this, 'stores')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• m² Başına Ciro Verimliliği</button>
                        </div>
                    </div>

                    <!-- 4.3 Taze Ürünler -->
                    <div>
                        <button onclick="toggleL2('l2_fresh', 'fresh')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_fresh">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-drumstick-bite text-xs text-emerald-400 w-4 text-center"></i>
                                <span>Taze Ürünler</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_fresh"></i>
                        </button>
                        <div id="sub-l2_fresh" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'fresh')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Kasap Karkas Randımanı</button>
                            <button onclick="selectL3(this, 'fresh')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Meyve-Sebze Ayıklama Kaybı</button>
                            <button onclick="selectL3(this, 'fresh')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Gün İçi Dinamik Tasfiye</button>
                        </div>
                    </div>

                    <!-- 4.4 Fire ve İmha -->
                    <div>
                        <button onclick="toggleL2('l2_waste', 'fresh')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_waste">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-trash-can text-xs text-rose-400 w-4 text-center"></i>
                                <span>Fire ve İmha</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_waste"></i>
                        </button>
                        <div id="sub-l2_waste" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'fresh')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Günlük SKT Fire Kayıtları</button>
                            <button onclick="selectL3(this, 'fresh')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Resmi İmha Tutanakları</button>
                        </div>
                    </div>

                    <!-- 4.5 Mağaza Denetimleri -->
                    <div>
                        <button onclick="toggleL2('l2_store_audits', 'store-audits')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_store_audits">
                            <div class="flex items-center gap-2">
                                <i class="fa-regular fa-file-lines text-xs text-blue-300 w-4 text-center"></i>
                                <span>Mağaza Denetimleri</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_store_audits"></i>
                        </button>
                        <div id="sub-l2_store_audits" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'store-audits')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Bölge Müdürü Denetim Formu</button>
                            <button onclick="selectL3(this, 'audit')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Mağaza Standart Puanları</button>
                        </div>
                    </div>

                    <!-- 4.6 Müşteri Deneyimi (YENİ EKLENDİ) -->
                    <div>
                        <button onclick="toggleL2('l2_store_cx', 'cx')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_store_cx">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-face-smile text-xs text-pink-400 w-4 text-center"></i>
                                <span>Müşteri Deneyimi</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_store_cx"></i>
                        </button>
                        <div id="sub-l2_store_cx" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'cx')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Şikayet & Geri Bildirim</button>
                            <button onclick="selectL3(this, 'cx')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Müşteri Memnuniyet Puanı (NPS)</button>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ========================================== -->
            <!-- 5. ANA MENÜ: FİNANS YÖNETİMİ (BAĞIMSIZ) -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_finance')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_finance">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs group-hover:bg-amber-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-coins"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Finans Yönetimi</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_finance"></i>
                </button>

                <!-- 5. Alt Menüler (L2) -->
                <div id="sub-l1_finance" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-amber-500/40">
                    <div>
                        <button onclick="toggleL2('l2_fin_vade', 'burden')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_fin_vade">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-file-invoice-dollar text-xs text-amber-400 w-4 text-center"></i><span>Tedarikçi Vade Açığı</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_fin_vade"></i>
                        </button>
                        <div id="sub-l2_fin_vade" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'burden')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Tedarikçi Vade Açığı Analizi</button>
                            <button onclick="selectL3(this, 'burden')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Nakit Kanaması Erken Uyarı</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_fin_ccc', 'burden')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_fin_ccc">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-arrows-rotate text-xs text-teal-400 w-4 text-center"></i><span>Nakit Dönüş Süresi (CCC)</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_fin_ccc"></i>
                        </button>
                        <div id="sub-l2_fin_ccc" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'burden')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Nakit Dönüş Döngüsü (DIO/DSO/DPO)</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_fin_cashflow', 'burden')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_fin_cashflow">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-cash-register text-xs text-emerald-400 w-4 text-center"></i><span>Nakit Akış & POS Tahsilat</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_fin_cashflow"></i>
                        </button>
                        <div id="sub-l2_fin_cashflow" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'burden')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Günlük POS Tahsilatı & Valör</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_fin_pnl', 'pnl-consolidation')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_fin_pnl">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-chart-pie text-xs text-rose-400 w-4 text-center"></i><span>Kâr-Zarar (P&L)</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_fin_pnl"></i>
                        </button>
                        <div id="sub-l2_fin_pnl" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'pnl-consolidation')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Kâr-Zarar (P&L) Konsolidasyonu</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ========================================== -->
            <!-- 6. ANA MENÜ: İNSAN KAYNAKLARI (BAĞIMSIZ) -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_hr')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_hr">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs group-hover:bg-blue-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-users"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">İnsan Kaynakları</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_hr"></i>
                </button>

                <!-- 6. Alt Menüler (L2) -->
                <div id="sub-l1_hr" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-blue-500/40">
                    <div>
                        <button onclick="toggleL2('l2_hr_org', 'hr')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_hr_org">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-sitemap text-xs text-blue-400 w-4 text-center"></i><span>Norm Kadro</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_hr_org"></i>
                        </button>
                        <div id="sub-l2_hr_org" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'hr')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Norm Kadro & Organizasyon</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_hr_shifts', 'hr')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_hr_shifts">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-calendar-week text-xs text-indigo-400 w-4 text-center"></i><span>Vardiya & Puantaj</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_hr_shifts"></i>
                        </button>
                        <div id="sub-l2_hr_shifts" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'hr')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Vardiya Çizelgesi & Puantaj</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_hr_turnover', 'hr')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_hr_turnover">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-arrow-trend-up text-xs text-amber-400 w-4 text-center"></i><span>Personel Devir Hızı</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_hr_turnover"></i>
                        </button>
                        <div id="sub-l2_hr_turnover" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'hr')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Personel Devir Hızı (Turnover)</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_hr_training', 'training-tracking')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_hr_training">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-user-graduate text-xs text-emerald-400 w-4 text-center"></i><span>Eğitim & Sertifika</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_hr_training"></i>
                        </button>
                        <div id="sub-l2_hr_training" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'training-tracking')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Eğitim & Sertifikasyon Takibi</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ========================================== -->
            <!-- 7. ANA MENÜ: TEKNİK BAKIM (BAĞIMSIZ) -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_maintenance')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_maintenance">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-orange-500/20 text-orange-400 flex items-center justify-center text-xs group-hover:bg-orange-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-wrench"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Teknik Bakım</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_maintenance"></i>
                </button>

                <!-- 7. Alt Menüler (L2) -->
                <div id="sub-l1_maintenance" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-orange-500/40">
                    <div>
                        <button onclick="toggleL2('l2_maint_cool', 'assets')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_maint_cool">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-snowflake text-xs text-cyan-400 w-4 text-center"></i><span>Soğutucu & Klima</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_maint_cool"></i>
                        </button>
                        <div id="sub-l2_maint_cool" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'assets')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Soğutucu Dolaplar & Klima</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_maint_assets', 'assets')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_maint_assets">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-scale-balanced text-xs text-amber-400 w-4 text-center"></i><span>Terazi & Demirbaş</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_maint_assets"></i>
                        </button>
                        <div id="sub-l2_maint_assets" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'assets')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Jeneratör, Terazi & Demirbaş</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_maint_sla', 'assets')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_maint_sla">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-headset text-xs text-rose-400 w-4 text-center"></i><span>Arıza & Servis SLA</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_maint_sla"></i>
                        </button>
                        <div id="sub-l2_maint_sla" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'assets')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Arıza Kayıtları & Servis SLA</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ========================================== -->
            <!-- 8. ANA MENÜ: BİLGİ TEKNOLOJİLERİ (BAĞIMSIZ) -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_it')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_it">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-laptop-code"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Bilgi Teknolojileri</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_it"></i>
                </button>

                <!-- 8. Alt Menüler (L2) -->
                <div id="sub-l1_it" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-indigo-500/40">
                    <div>
                        <button onclick="toggleL2('l2_it_erp', 'it')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_it_erp">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-server text-xs text-indigo-400 w-4 text-center"></i><span>ERP & POS</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_it_erp"></i>
                        </button>
                        <div id="sub-l2_it_erp" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'it')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• ERP & POS Entegrasyonları</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_it_roles', 'it')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_it_roles">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-user-shield text-xs text-blue-400 w-4 text-center"></i><span>Rol & Yetki Matrisi</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_it_roles"></i>
                        </button>
                        <div id="sub-l2_it_roles" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'it')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Rol & Yetki Matrisi</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_it_backup', 'it')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_it_backup">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-database text-xs text-emerald-400 w-4 text-center"></i><span>Yedek & Güvenlik</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_it_backup"></i>
                        </button>
                        <div id="sub-l2_it_backup" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'it')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Veritabanı Yedeği & Güvenlik</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ========================================== -->
            <!-- 9. ANA MENÜ: YATIRIM VE YENİ MAĞAZA (BAĞIMSIZ) -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_expansion')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_expansion">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs group-hover:bg-purple-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-building"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Yatırım ve Yeni Mağaza</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_expansion"></i>
                </button>

                <!-- 9. Alt Menüler (L2) -->
                <div id="sub-l1_expansion" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-purple-500/40">
                    <div>
                        <button onclick="toggleL2('l2_exp_feasibility', 'expansion')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_exp_feasibility">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-map-location-dot text-xs text-purple-400 w-4 text-center"></i><span>Fizibilite & Lokasyon</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_exp_feasibility"></i>
                        </button>
                        <div id="sub-l2_exp_feasibility" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'expansion')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Yeni Lokasyon Fizibilitesi</button>
                            <button onclick="selectL3(this, 'expansion')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Açılış Bütçesi & CAPEX</button>
                        </div>
                    </div>
                    <div>
                        <button onclick="toggleL2('l2_exp_closing', 'store-closing')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_exp_closing">
                            <div class="flex items-center gap-2"><i class="fa-solid fa-door-closed text-xs text-rose-400 w-4 text-center"></i><span>Kapanış & Devir</span></div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_exp_closing"></i>
                        </button>
                        <div id="sub-l2_exp_closing" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'store-closing')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Şube Kapanış/Devir Değerlendirmesi</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ========================================== -->
            <!-- 10. ANA MENÜ: RİSK VE UYUM -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_risk')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_risk">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center text-xs group-hover:bg-rose-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-shield-halved"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Risk ve Uyum</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_risk"></i>
                </button>

                <!-- 10. Alt Menüler (L2) -->
                <div id="sub-l1_risk" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-rose-500/40">
                    
                    <!-- 10.1 Kalite ve Gıda Güvenliği -->
                    <div>
                        <button onclick="toggleL2('l2_risk_quality', 'quality')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_risk_quality">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-shield-halved text-xs text-emerald-400 w-4 text-center"></i>
                                <span>Kalite ve Gıda Güvenliği</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_risk_quality"></i>
                        </button>
                        <div id="sub-l2_risk_quality" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'quality')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• HACCP Sıcaklık & Soğuk Zincir</button>
                            <button onclick="selectL3(this, 'quality')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Numune & Laboratuvar Sonuçları</button>
                        </div>
                    </div>

                    <!-- 10.2 Kayıp Önleme -->
                    <div>
                        <button onclick="toggleL2('l2_risk_loss', 'audit')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_risk_loss">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-triangle-exclamation text-xs text-rose-400 w-4 text-center"></i>
                                <span>Kayıp Önleme</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_risk_loss"></i>
                        </button>
                        <div id="sub-l2_risk_loss" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'audit')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Kasa Açık / Fazla Raporu</button>
                            <button onclick="selectL3(this, 'audit')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Şüpheli İptal & İade Analizleri</button>
                            <button onclick="selectL3(this, 'inventory-variance')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Envanter Sayım Farkı Analizi</button>
                        </div>
                    </div>

                    <!-- 10.3 Sözleşme ve Yasal Uyum -->
                    <div>
                        <button onclick="toggleL2('l2_risk_contracts', 'contracts')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_risk_contracts">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-file-contract text-xs text-blue-400 w-4 text-center"></i>
                                <span>Sözleşme ve Yasal Uyum</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_risk_contracts"></i>
                        </button>
                        <div id="sub-l2_risk_contracts" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'contracts')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Tedarikçi Sözleşmeleri</button>
                            <button onclick="selectL3(this, 'contracts')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Mağaza Kira Sözleşmeleri</button>
                            <button onclick="selectL3(this, 'permits')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • Ruhsat & Resmi İzin Takibi</button>
                        </div>
                    </div>

                    <!-- 10.4 İş Sağlığı ve Güvenliği -->
                    <div>
                        <button onclick="toggleL2('l2_risk_isg', 'quality')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_risk_isg">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-helmet-safety text-xs text-amber-400 w-4 text-center"></i>
                                <span>İş Sağlığı ve Güvenliği</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_risk_isg"></i>
                        </button>
                        <div id="sub-l2_risk_isg" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'quality')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• İSG Risk Analiz Formları</button>
                            <button onclick="selectL3(this, 'quality')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Periyodik Yangın/İlk Yardım</button>
                            <button onclick="selectL3(this, 'work-accidents')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🆕 • İş Kazası Kayıt Defteri</button>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ========================================== -->
            <!-- 11. ANA MENÜ: BAĞLI PLATFORMLAR -->
            <!-- ========================================== -->
            <div class="menu-l1-group">
                <button onclick="toggleL1('l1_platforms')" class="l1-btn w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold text-white bg-slate-800/90 hover:bg-slate-700/90 transition-all text-left border border-slate-700/60 shadow-xs cursor-pointer group" id="btn-l1_platforms">
                    <div class="flex items-center gap-2.5">
                        <div class="w-6 h-6 rounded-lg bg-pink-500/20 text-pink-400 flex items-center justify-center text-xs group-hover:bg-pink-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-network-wired"></i>
                        </div>
                        <span class="text-slate-100 font-bold text-xs">Bağlı Platformlar</span>
                    </div>
                    <i class="fa-solid fa-chevron-down text-[10px] text-slate-400 transition-transform duration-200" id="chevron-l1_platforms"></i>
                </button>

                <!-- 11. Alt Menüler (L2) -->
                <div id="sub-l1_platforms" class="hidden pl-2.5 pr-1 py-1 space-y-1 bg-black/25 rounded-xl mt-1 border-l-2 border-pink-500/40">
                    
                    <!-- 11.1 XPlusCRM -->
                    <div>
                        <button onclick="toggleL2('l2_crm', 'crm')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_crm">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-users-viewfinder text-xs text-rose-400 w-4 text-center"></i>
                                <span>XPlusCRM</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_crm"></i>
                        </button>
                        <div id="sub-l2_crm" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'crm')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Fazla Stok Tasfiye Simülatörü</button>
                            <button onclick="selectL3(this, 'crm')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Sadık Alıcı Segmentleri (RFM)</button>
                        </div>
                    </div>

                    <!-- 11.2 Perakende Kariyer Akademisi -->
                    <div>
                        <button onclick="toggleL2('l2_academy', 'academy')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_academy">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-graduation-cap text-xs text-sky-400 w-4 text-center"></i>
                                <span>Perakende Kariyer Akademisi</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_academy"></i>
                        </button>
                        <div id="sub-l2_academy" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <a href="https://www.perakendekariyerakademisi.com" target="_blank" class="l3-btn w-full text-left py-1 px-2 rounded-md text-sky-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">🌐 www.perakendekariyerakademisi.com ↗</a>
                            <button onclick="selectL3(this, 'academy')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Yetkinlik & Beceri Matrisi</button>
                            <button onclick="selectL3(this, 'academy')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Zorunlu Kurs Atama Masası</button>
                        </div>
                    </div>

                    <!-- 11.3 PerakendeData -->
                    <div>
                        <button onclick="toggleL2('l2_perakendedata', 'macro')" class="l2-btn w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all text-left cursor-pointer" id="btn-l2_perakendedata">
                            <div class="flex items-center gap-2">
                                <i class="fa-solid fa-earth-europe text-xs text-cyan-400 w-4 text-center"></i>
                                <span>PerakendeData</span>
                            </div>
                            <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 transition-transform duration-200" id="chevron-l2_perakendedata"></i>
                        </button>
                        <div id="sub-l2_perakendedata" class="hidden pl-6 pr-1 py-1 space-y-0.5 text-xs">
                            <button onclick="selectL3(this, 'macro')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Gıda Enflasyonu & TÜFE</button>
                            <button onclick="selectL3(this, 'macro')" class="l3-btn w-full text-left py-1 px-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors block font-medium">• Sektör Büyüme Göstergeleri</button>
                        </div>
                    </div>

                </div>
            </div>"""

# Replace the sidebar menu in html
sb_pattern = re.compile(r'<div class="p-3 space-y-2 flex-1 overflow-y-auto custom-scrollbar" id="sidebarMenu">.*?</div>\s*<!-- Sol Menü Alt Bilgi', re.DOTALL)
if sb_pattern.search(html):
    html = sb_pattern.sub(new_sidebar_menu + "\n\n        <!-- Sol Menü Alt Bilgi", html)
    print("Sidebar successfully replaced!")
else:
    print("WARNING: sidebar pattern match failed, trying alternative slice")
    start_idx = html.find('<div class="p-3 space-y-2 flex-1 overflow-y-auto custom-scrollbar" id="sidebarMenu">')
    end_idx = html.find('<!-- Sol Menü Alt Bilgi & Kullanıcı -->', start_idx)
    html = html[:start_idx] + new_sidebar_menu + "\n\n        " + html[end_idx:]
    print("Sidebar replaced via index slice!")

with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Step 1 complete: Sidebar menu updated!")
