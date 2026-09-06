# -*- coding: utf-8 -*-
"""
Adds PDF and Word export features to all Decision / Meeting views in dashboard.html
"""
import re

SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Toplantılar Karar Özeti header buttons
old_sum_hdr_btn = """                <div class="flex items-center gap-2.5">
                    <span class="bg-indigo-500/20 text-indigo-300 text-xs px-3 py-1.5 rounded-xl border border-indigo-500/30 flex items-center gap-1.5 font-bold">
                        <i class="fa-solid fa-lock text-amber-400"></i> Salt-Okunur (Read-Only)
                    </span>
                    <button onclick="filterMeetingsSummary()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-3.5 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-rotate-right"></i> Yenile
                    </button>
                </div>"""

new_sum_hdr_btn = """                <div class="flex flex-wrap items-center gap-2">
                    <span class="bg-indigo-500/20 text-indigo-300 text-xs px-3 py-1.5 rounded-xl border border-indigo-500/30 flex items-center gap-1.5 font-bold">
                        <i class="fa-solid fa-lock text-amber-400"></i> Salt-Okunur
                    </span>
                    <button onclick="exportDecisionsToPDF('summary', 'Konsolide Toplantılar Karar Özeti Raporu')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer" title="PDF Olarak İndir / Yazdır">
                        <i class="fa-solid fa-file-pdf"></i> PDF İndir
                    </button>
                    <button onclick="exportDecisionsToWord('summary', 'Konsolide Toplantılar Karar Özeti Raporu')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer" title="Word Belgesi (.doc) Olarak İndir">
                        <i class="fa-solid fa-file-word"></i> Word İndir
                    </button>
                    <button onclick="filterMeetingsSummary()" class="bg-slate-700 hover:bg-slate-600 text-white font-bold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-rotate-right"></i> Yenile
                    </button>
                </div>"""

if old_sum_hdr_btn in html:
    html = html.replace(old_sum_hdr_btn, new_sum_hdr_btn)
    print("Summary header buttons updated!")
else:
    print("Warning: old_sum_hdr_btn not matched directly")

# 2. Update İcra Kurulu Header
old_icra_btn = """                <div>
                    <button onclick="openActionDecisionModal('', 'İcra Kurulu Toplantısı', currentIcraQuarter, 'İcra Kurulu')" class="bg-purple-500 hover:bg-purple-400 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni İcra Kararı Ekle
                    </button>
                </div>"""

new_icra_btn = """                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="exportDecisionsToPDF('icra', 'İcra Kurulu Toplantı Kararları ve Tutanağı')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-pdf"></i> PDF İndir
                    </button>
                    <button onclick="exportDecisionsToWord('icra', 'İcra Kurulu Toplantı Kararları ve Tutanağı')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-word"></i> Word İndir
                    </button>
                    <button onclick="openActionDecisionModal('', 'İcra Kurulu Toplantısı', currentIcraQuarter, 'İcra Kurulu')" class="bg-purple-500 hover:bg-purple-400 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni İcra Kararı
                    </button>
                </div>"""

if old_icra_btn in html:
    html = html.replace(old_icra_btn, new_icra_btn)
    print("Icra header buttons updated!")

# 3. Update Purchasing Header
old_pur_btn = """                <div>
                    <button onclick="openActionDecisionModal('', 'Satınalma & Kategori Toplantısı', `${currentPurchasingMonth} - ${currentPurchasingWeek}`, 'Satın Alma')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Satınalma Kararı Ekle
                    </button>
                </div>"""

new_pur_btn = """                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="exportDecisionsToPDF('purchasing', 'Satınalma & Kategori Toplantı Kararları')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-pdf"></i> PDF İndir
                    </button>
                    <button onclick="exportDecisionsToWord('purchasing', 'Satınalma & Kategori Toplantı Kararları')" class="bg-blue-700 hover:bg-blue-600 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-word"></i> Word İndir
                    </button>
                    <button onclick="openActionDecisionModal('', 'Satınalma & Kategori Toplantısı', `${currentPurchasingMonth} - ${currentPurchasingWeek}`, 'Satın Alma')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Karar
                    </button>
                </div>"""

if old_pur_btn in html:
    html = html.replace(old_pur_btn, new_pur_btn)
    print("Purchasing header buttons updated!")

# 4. Update Field Header
old_fld_btn = """                <div>
                    <button onclick="openActionDecisionModal('', 'Saha & Satış Değerlendirme', `${currentFieldMonth} - ${currentFieldWeek}`, 'Saha Operasyon')" class="bg-teal-600 hover:bg-teal-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Saha Kararı Ekle
                    </button>
                </div>"""

new_fld_btn = """                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="exportDecisionsToPDF('field', 'Saha & Satış Değerlendirme Toplantı Kararları')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-pdf"></i> PDF İndir
                    </button>
                    <button onclick="exportDecisionsToWord('field', 'Saha & Satış Değerlendirme Toplantı Kararları')" class="bg-teal-700 hover:bg-teal-600 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-word"></i> Word İndir
                    </button>
                    <button onclick="openActionDecisionModal('', 'Saha & Satış Değerlendirme', `${currentFieldMonth} - ${currentFieldWeek}`, 'Saha Operasyon')" class="bg-teal-600 hover:bg-teal-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Karar
                    </button>
                </div>"""

if old_fld_btn in html:
    html = html.replace(old_fld_btn, new_fld_btn)
    print("Field header buttons updated!")

# 5. Update Toplantı Karar Takibi Header
old_tr_btn = """                <div>
                    <button onclick="openActionDecisionModal('', 'Toplantı Karar Takibi', '', '')" class="bg-purple-600 hover:bg-purple-500 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Toplantı Kararı Aç
                    </button>
                </div>"""

new_tr_btn = """                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="exportDecisionsToPDF('tracking', 'Toplantı Karar Takip Raporu')" class="bg-rose-600 hover:bg-rose-500 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-pdf"></i> PDF İndir
                    </button>
                    <button onclick="exportDecisionsToWord('tracking', 'Toplantı Karar Takip Raporu')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer">
                        <i class="fa-solid fa-file-word"></i> Word İndir
                    </button>
                    <button onclick="openActionDecisionModal('', 'Toplantı Karar Takibi', '', '')" class="bg-purple-600 hover:bg-purple-500 text-white font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer">
                        <i class="fa-solid fa-plus"></i> Yeni Karar Aç
                    </button>
                </div>"""

if old_tr_btn in html:
    html = html.replace(old_tr_btn, new_tr_btn)
    print("Tracking header buttons updated!")

# 6. Add JavaScript Export Functions
export_js = """
        // =========================================================================
        // 🆕 KARARLARI PDF VE WORD DÖKÜMANI OLARAK DIŞA AKTARMA (EXPORT) MOTORU
        // =========================================================================
        function getScopedDecisions(scope) {
            if (scope === 'icra') {
                return {
                    title: `İcra Kurulu Toplantı Kararları (${currentIcraQuarter})`,
                    period: currentIcraQuarter,
                    records: actionDecisionStore.filter(r => r.sourceModule === 'İcra Kurulu Toplantısı' && r.period === currentIcraQuarter)
                };
            } else if (scope === 'purchasing') {
                const p = `${currentPurchasingMonth} - ${currentPurchasingWeek}`;
                return {
                    title: `Satınalma & Kategori Toplantı Kararları (${p})`,
                    period: p,
                    records: actionDecisionStore.filter(r => r.sourceModule === 'Satınalma & Kategori Toplantısı' && (r.period === p || r.period.includes(currentPurchasingMonth)))
                };
            } else if (scope === 'field') {
                const p = `${currentFieldMonth} - ${currentFieldWeek}`;
                return {
                    title: `Saha & Satış Değerlendirme Kararları (${p})`,
                    period: p,
                    records: actionDecisionStore.filter(r => r.sourceModule === 'Saha & Satış Değerlendirme' && (r.period === p || r.period.includes(currentFieldMonth)))
                };
            } else if (scope === 'tracking') {
                return {
                    title: `Toplantı Karar Takip Çizelgesi`,
                    period: 'Tüm Dönemler',
                    records: actionDecisionStore.filter(r => r.sourceModule.includes('Toplantı') || r.sourceModule.includes('İcra') || r.sourceModule.includes('Saha'))
                };
            } else {
                // 'summary' - uses current filtered list from summary table
                const role = document.getElementById('summaryRoleSimulator')?.value || 'EXECUTIVE';
                return {
                    title: `Konsolide Toplantılar Karar Özeti Raporu`,
                    period: 'Konsolide / Tüm Dönemler',
                    records: actionDecisionStore
                };
            }
        }

        // 1. PDF Olarak İndir / Yazdır (Yüksek Kaliteli Kurumsal Belge Şablonu)
        function exportDecisionsToPDF(scope, customTitle) {
            const data = getScopedDecisions(scope);
            const title = customTitle || data.title;
            const records = data.records;
            const todayStr = '06.09.2026'; // Sistem tarihi

            const printWindow = window.open('', '_blank', 'width=1000,height=800');
            if (!printWindow) {
                alert('Lütfen açılır pencerelere (pop-up) izin veriniz.');
                return;
            }

            const rowsHtml = records.map((r, i) => `
                <tr style="border-bottom: 1px solid #e2e8f0; font-size: 11px;">
                    <td style="padding: 8px 6px; text-align: center; font-weight: bold; color: #64748b;">${i + 1}</td>
                    <td style="padding: 8px 6px; font-weight: bold; color: #0f172a;">${r.actionDecision}</td>
                    <td style="padding: 8px 6px; color: #334155;">${r.sourceModule}<br><small style="color:#64748b;">${r.period || '—'}</small></td>
                    <td style="padding: 8px 6px; color: #334155;">${r.unit}</td>
                    <td style="padding: 8px 6px; font-weight: 600; color: #1e293b;">${r.assignee}</td>
                    <td style="padding: 8px 6px; color: #475569; white-space: nowrap;">${r.startDate} &rarr; <b>${r.endDate}</b></td>
                    <td style="padding: 8px 6px; text-align: center;">
                        <span style="display:inline-block; padding: 2px 8px; border-radius: 9999px; font-weight: bold; font-size: 10px; ${
                            r.status === 'Yapıldı' ? 'background: #dcfce7; color: #166534;' :
                            r.status === 'Beklemede' ? 'background: #fef3c7; color: #92400e;' : 'background: #dbeafe; color: #1e40af;'
                        }">${r.status}</span>
                    </td>
                    <td style="padding: 8px 6px; font-size: 10px; color: #475569;">${r.resultReason || '—'}</td>
                </tr>
            `).join('');

            printWindow.document.write(`
                <!DOCTYPE html>
                <html lang="tr">
                <head>
                    <meta charset="UTF-8">
                    <title>${title} - MarketYönetimi360</title>
                    <style>
                        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; color: #0f172a; }
                        .header-box { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e40af; padding-bottom: 12px; margin-bottom: 16px; }
                        .logo-text { font-size: 20px; font-weight: 900; color: #0f172a; }
                        .logo-tag { background: #2563eb; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-left: 4px; }
                        .meta-box { font-size: 11px; color: #475569; line-height: 1.4; text-align: right; }
                        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                        th { background: #f1f5f9; color: #334155; font-size: 11px; font-weight: bold; padding: 8px 6px; border-bottom: 2px solid #cbd5e1; text-align: left; }
                        .footer { margin-top: 30px; display: flex; justify-content: space-between; font-size: 11px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 15px; }
                        .sig-box { width: 200px; text-align: center; }
                        .sig-line { border-bottom: 1px dashed #94a3b8; height: 35px; margin-bottom: 4px; }
                        @media print {
                            button { display: none !important; }
                            body { margin: 0; }
                        }
                    </style>
                </head>
                <body>
                    <div style="text-align: right; margin-bottom: 10px;">
                        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer;">🖨️ Yazdır / PDF Kaydet</button>
                    </div>
                    <div class="header-box">
                        <div>
                            <div class="logo-text">MarketYönetimi<span class="logo-tag">360</span></div>
                            <h2 style="margin: 4px 0 0 0; font-size: 16px; color: #1e3a8a;">${title}</h2>
                        </div>
                        <div class="meta-box">
                            <div><b>Rapor Tarihi:</b> ${todayStr}</div>
                            <div><b>Dönem / Kapsam:</b> ${data.period}</div>
                            <div><b>Toplam Karar Adedi:</b> ${records.length} Kayıt</div>
                        </div>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th style="width: 25px; text-align: center;">#</th>
                                <th>Alınan Karar / Aksiyon</th>
                                <th>Kaynak</th>
                                <th>Birim</th>
                                <th>Sorumlu</th>
                                <th>Süre</th>
                                <th style="text-align: center;">Durum</th>
                                <th>Sonuç / Gerekçe</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>

                    <div class="footer">
                        <div>MarketYönetimi360 Kurumsal Karar Destek Masası tarafından üretilmiştir.</div>
                        <div style="display: flex; gap: 40px;">
                            <div class="sig-box">
                                <div class="sig-line"></div>
                                <div><b>Toplantı Başkanı / Yönetici</b></div>
                            </div>
                            <div class="sig-box">
                                <div class="sig-line"></div>
                                <div><b>Raportör / İcra Sekreteryası</b></div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            `);
            printWindow.document.close();
            setTimeout(() => {
                printWindow.print();
            }, 300);
            showToast(`${title} PDF formatında hazırlandı.`, "success");
        }

        // 2. Word (.doc) Olarak İndir (Microsoft Word Uyumlu HTML/XML Blob)
        function exportDecisionsToWord(scope, customTitle) {
            const data = getScopedDecisions(scope);
            const title = customTitle || data.title;
            const records = data.records;
            const todayStr = '06.09.2026';

            const rowsHtml = records.map((r, i) => `
                <tr style="border-bottom: 1px solid #d1d5db;">
                    <td style="padding: 8px; text-align: center; font-weight: bold;">${i + 1}</td>
                    <td style="padding: 8px; font-weight: bold;">${r.actionDecision}</td>
                    <td style="padding: 8px;">${r.sourceModule} (${r.period || '—'})</td>
                    <td style="padding: 8px;">${r.unit}</td>
                    <td style="padding: 8px; font-weight: 600;">${r.assignee}</td>
                    <td style="padding: 8px;">${r.startDate} &rarr; <b>${r.endDate}</b></td>
                    <td style="padding: 8px; text-align: center; font-weight: bold;">${r.status}</td>
                    <td style="padding: 8px;">${r.resultReason || '—'}</td>
                </tr>
            `).join('');

            const wordHtml = `
                <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
                <head>
                    <meta charset='utf-8'>
                    <title>${title}</title>
                    <style>
                        body { font-family: 'Calibri', 'Arial', sans-serif; font-size: 11pt; color: #111827; }
                        h1 { color: #1e3a8a; font-size: 18pt; margin-bottom: 4px; }
                        .meta { font-size: 10pt; color: #4b5563; margin-bottom: 16px; }
                        table { width: 100%; border-collapse: collapse; font-size: 10pt; }
                        th { background-color: #f3f4f6; color: #1f2937; padding: 8px; border: 1px solid #9ca3af; text-align: left; }
                        td { border: 1px solid #d1d5db; padding: 6px 8px; }
                    </style>
                </head>
                <body>
                    <h1>MarketYönetimi360 — ${title}</h1>
                    <div class="meta">
                        <p><b>Rapor Tarihi:</b> ${todayStr} | <b>Kapsam / Dönem:</b> ${data.period} | <b>Toplam Karar:</b> ${records.length}</p>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 30px;">#</th>
                                <th>Alınan Karar / Aksiyon</th>
                                <th>Kaynak Modül</th>
                                <th>Birim</th>
                                <th>Sorumlu</th>
                                <th>Süre</th>
                                <th>Durum</th>
                                <th>Sonuç / Gerekçe</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                    <br><br>
                    <table style="width: 100%; border: none;">
                        <tr style="border: none;">
                            <td style="border: none; width: 50%; text-align: center;">
                                <p>_______________________________</p>
                                <p><b>Toplantı Başkanı</b></p>
                            </td>
                            <td style="border: none; width: 50%; text-align: center;">
                                <p>_______________________________</p>
                                <p><b>İcra Sekreteryası / Raportör</b></p>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
            `;

            const blob = new Blob(['\ufeff' + wordHtml], {
                type: 'application/msword'
            });

            const fileName = `${title.replace(/[\s\/]+/g, '_')}_${todayStr}.doc`;
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);

            showToast(`${fileName} Word formatında başarıyla indirildi!`, "success");
        }
"""

if 'function exportDecisionsToPDF' not in html:
    # Insert before getRemainingDaysBadge or renderActionDecisionTable
    target_pos = html.find('function getRemainingDaysBadge')
    if target_pos != -1:
        html = html[:target_pos] + export_js + "\n        " + html[target_pos:]
        print("Export JS functions added successfully!")
    else:
        print("Warning: target_pos for export_js not found!")

with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Export features applied successfully!")
