# -*- coding: utf-8 -*-
"""
Removes all duplicate export functions from dashboard.html and installs a single, robust
filtered export engine supporting PDF, Word, and Excel.
"""
import re

SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Locate where getScopedDecisions appears and clean up all duplicates
# We want only ONE definition of exportDecisionsToPDF, exportDecisionsToWord, exportDecisionsToExcel, and getScopedDecisions

# Let's find the start of the first export block
first_marker = "// =========================================================================" + "\n" + "        // 🆕 KARARLARI PDF, WORD VE EXCEL DÖKÜMANI OLARAK DIŞA AKTARMA MOTORU"
if first_marker not in html:
    first_marker = "// =========================================================================" + "\n" + "        // 🆕 KARARLARI PDF VE WORD DÖKÜMANI OLARAK DIŞA AKTARMA (EXPORT) MOTORU"

# Find renderActionDecisionTable or getRemainingDaysBadge as the anchor
render_table_anchor = "        // Genel Yeniden Kullanılabilir Tablo Render Fonksiyonu\n        function renderActionDecisionTable"

clean_export_engine = """        // =========================================================================
        // 🆕 KARARLARI PDF, WORD VE EXCEL DÖKÜMANI OLARAK DIŞA AKTARMA MOTORU
        // (Filtrelenen birim ve kriterlere göre özel başlık ve veri seti üretir)
        // =========================================================================
        function getScopedDecisions(scope) {
            if (scope === 'icra') {
                const recs = actionDecisionStore.filter(r => r.sourceModule === 'İcra Kurulu Toplantısı' && r.period === currentIcraQuarter);
                return {
                    title: `İcra Kurulu — ${currentIcraQuarter} Toplantı Karar Özeti`,
                    unitName: 'İcra Kurulu',
                    period: currentIcraQuarter,
                    filterInfo: `Dönem: ${currentIcraQuarter}`,
                    records: recs
                };
            } else if (scope === 'purchasing') {
                const p = `${currentPurchasingMonth} - ${currentPurchasingWeek}`;
                const recs = actionDecisionStore.filter(r => r.sourceModule === 'Satınalma & Kategori Toplantısı' && (r.period === p || r.period.includes(currentPurchasingMonth)));
                return {
                    title: `Satın Alma Birimi — ${p} Toplantı Karar Özeti`,
                    unitName: 'Satın Alma',
                    period: p,
                    filterInfo: `Ay: ${currentPurchasingMonth}, Hafta: ${currentPurchasingWeek}`,
                    records: recs
                };
            } else if (scope === 'field') {
                const p = `${currentFieldMonth} - ${currentFieldWeek}`;
                const recs = actionDecisionStore.filter(r => r.sourceModule === 'Saha & Satış Değerlendirme' && (r.period === p || r.period.includes(currentFieldMonth)));
                return {
                    title: `Saha Operasyon — ${p} Toplantı Karar Özeti`,
                    unitName: 'Saha Operasyon',
                    period: p,
                    filterInfo: `Ay: ${currentFieldMonth}, Hafta: ${currentFieldWeek}`,
                    records: recs
                };
            } else if (scope === 'tracking') {
                const recs = actionDecisionStore.filter(r => r.sourceModule.includes('Toplantı') || r.sourceModule.includes('İcra') || r.sourceModule.includes('Saha'));
                return {
                    title: `Yönetim Toplantıları — Karar Takip Özeti`,
                    unitName: 'Tüm Birimler',
                    period: 'Tüm Dönemler',
                    filterInfo: 'Kapsam: Yönetim Toplantı Kararları',
                    records: recs
                };
            } else {
                // 'summary' - SEÇİLEN BİRİM VE FİLTREYE GÖRE TAM DİNAMİK FİLTRELEME
                const role = document.getElementById('summaryRoleSimulator')?.value || 'EXECUTIVE';
                const source = document.getElementById('sumFilterSource')?.value || '';
                const unit = document.getElementById('sumFilterUnit')?.value || '';
                const status = document.getElementById('sumFilterStatus')?.value || '';
                const period = document.getElementById('sumFilterPeriod')?.value || '';
                const assignee = document.getElementById('sumFilterAssignee')?.value || '';
                const search = (document.getElementById('sumFilterSearch')?.value || '').toLowerCase().trim();

                const roleNameMap = {
                    'EXECUTIVE': 'Genel Müdür / İcra Kurulu',
                    'FIELD_MANAGER': 'Bölge / Saha Müdürü',
                    'PURCHASING_MANAGER': 'Satınalma / Kategori Müdürü',
                    'UNIT_RESPONSIBLE': 'Birim Sorumlusu',
                    'EMPLOYEE': 'Genel Çalışan (Ahmet Kılıç)'
                };

                const filterDescriptions = [];
                filterDescriptions.push(`Aktif Rol: ${roleNameMap[role] || role}`);
                if (unit) filterDescriptions.push(`Seçilen Birim: ${unit}`);
                if (source) filterDescriptions.push(`Kaynak: ${source}`);
                if (status) filterDescriptions.push(`Durum: ${status}`);
                if (period) filterDescriptions.push(`Dönem: ${period}`);
                if (assignee) filterDescriptions.push(`Sorumlu: ${assignee}`);
                if (search) filterDescriptions.push(`Arama: "${search}"`);

                let filtered = actionDecisionStore.filter(r => {
                    // 1. Rol bazlı filtreleme
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
                        if (r.assignee !== 'Ahmet Kılıç') return false;
                    }

                    // 2. Form Kriterleri (Birim, Kaynak, Durum, Dönem, Sorumlu, Arama)
                    if (source && r.sourceModule !== source) return false;
                    if (unit && r.unit !== unit) return false;
                    if (status && r.status !== status) return false;
                    if (period && r.period !== period && !r.period.includes(period)) return false;
                    if (assignee && r.assignee !== assignee) return false;
                    if (search && !r.actionDecision.toLowerCase().includes(search) && !r.resultReason.toLowerCase().includes(search)) return false;

                    return true;
                });

                // Başlık Üretimi: Birim seçilmişse (örn: Satın Alma) mutlaka birim adını başlığa koy
                let docTitle = 'Toplantılar Karar Özeti';
                if (unit) {
                    docTitle = `${unit} Birimi — Toplantı Karar Özeti`;
                } else if (source) {
                    docTitle = `${source} — Karar Özeti`;
                } else if (role === 'PURCHASING_MANAGER') {
                    docTitle = `Satın Alma & Kategori — Toplantı Karar Özeti`;
                } else if (role === 'FIELD_MANAGER') {
                    docTitle = `Saha Operasyon & Satış — Toplantı Karar Özeti`;
                } else {
                    docTitle = `Konsolide Toplantılar Karar Özeti Raporu`;
                }

                return {
                    title: docTitle,
                    unitName: unit || 'Tüm Birimler',
                    period: period || 'Tüm Dönemler',
                    filterInfo: filterDescriptions.join(' | '),
                    records: filtered
                };
            }
        }

        // 1. PDF Olarak İndir / Yazdır (Filtrelenen Kısmı Döker)
        function exportDecisionsToPDF(scope, customTitle) {
            const data = getScopedDecisions(scope);
            const title = customTitle || data.title;
            const records = data.records;
            const todayStr = '06.09.2026';

            if (!records || records.length === 0) {
                showToast("Filtreleme sonucunda indirilecek kayıt bulunamadı!", "warning");
                return;
            }

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
                    <td style="padding: 8px 6px; color: #334155;"><span style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:bold;">${r.unit}</span></td>
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
                        .header-box { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e40af; padding-bottom: 12px; margin-bottom: 12px; }
                        .logo-text { font-size: 20px; font-weight: 900; color: #0f172a; }
                        .logo-tag { background: #2563eb; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-left: 4px; }
                        .meta-box { font-size: 11px; color: #475569; line-height: 1.4; text-align: right; }
                        .filter-badge-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px 10px; font-size: 11px; color: #1e293b; margin-bottom: 12px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 6px; }
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
                            <div><b>Filtrelenen Karar Sayısı:</b> <b>${records.length} Kayıt</b></div>
                        </div>
                    </div>

                    ${data.filterInfo ? `<div class="filter-badge-box"><b>🔍 Filtre Kriterleri:</b> ${data.filterInfo}</div>` : ''}

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
                        <div>MarketYönetimi360 Kurumsal Karar Destek Masası tarafından filtrelenmiş verilerle üretilmiştir.</div>
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
            showToast(`${title} (${records.length} kayıt) PDF formatında hazırlandı.`, "success");
        }

        // 2. Word (.doc) Olarak İndir (Filtrelenen Kısmı Döker)
        function exportDecisionsToWord(scope, customTitle) {
            const data = getScopedDecisions(scope);
            const title = customTitle || data.title;
            const records = data.records;
            const todayStr = '06.09.2026';

            if (!records || records.length === 0) {
                showToast("Filtreleme sonucunda indirilecek kayıt bulunamadı!", "warning");
                return;
            }

            const rowsHtml = records.map((r, i) => `
                <tr style="border-bottom: 1px solid #d1d5db;">
                    <td style="padding: 8px; text-align: center; font-weight: bold;">${i + 1}</td>
                    <td style="padding: 8px; font-weight: bold;">${r.actionDecision}</td>
                    <td style="padding: 8px;">${r.sourceModule} (${r.period || '—'})</td>
                    <td style="padding: 8px;"><b>${r.unit}</b></td>
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
                        .meta { font-size: 10pt; color: #4b5563; margin-bottom: 12px; }
                        .filter-info { background-color: #f3f4f6; border: 1px solid #d1d5db; padding: 6px 10px; font-size: 9.5pt; margin-bottom: 14px; }
                        table { width: 100%; border-collapse: collapse; font-size: 10pt; }
                        th { background-color: #f3f4f6; color: #1f2937; padding: 8px; border: 1px solid #9ca3af; text-align: left; }
                        td { border: 1px solid #d1d5db; padding: 6px 8px; }
                    </style>
                </head>
                <body>
                    <h1>MarketYönetimi360 — ${title}</h1>
                    <div class="meta">
                        <p><b>Rapor Tarihi:</b> ${todayStr} | <b>Filtrelenen Karar Adedi:</b> ${records.length} Kayıt</p>
                    </div>
                    ${data.filterInfo ? `<div class="filter-info"><b>Uygulanan Filtre Kriterleri:</b> ${data.filterInfo}</div>` : ''}
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

            const blob = new Blob(['\\ufeff' + wordHtml], {
                type: 'application/msword'
            });

            const cleanFileName = `${title.replace(/[\\s\\/—]+/g, '_')}_${todayStr}.doc`;
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = cleanFileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);

            showToast(`${cleanFileName} Word formatında başarıyla indirildi!`, "success");
        }

        // 3. Excel (.xls) Olarak İndir (Filtrelenen Kısmı Döker)
        function exportDecisionsToExcel(scope, customTitle) {
            const data = getScopedDecisions(scope);
            const title = customTitle || data.title;
            const records = data.records;
            const todayStr = '06.09.2026';

            if (!records || records.length === 0) {
                showToast("Filtreleme sonucunda indirilecek kayıt bulunamadı!", "warning");
                return;
            }

            const rowsHtml = records.map((r, i) => `
                <tr>
                    <td style="text-align:center;">${i + 1}</td>
                    <td>${r.sourceModule}</td>
                    <td>${r.period || '—'}</td>
                    <td>${r.meetingDate || '—'}</td>
                    <td><b>${r.unit}</b></td>
                    <td>${r.actionDecision}</td>
                    <td>${r.assignee}</td>
                    <td>${r.startDate}</td>
                    <td>${r.endDate}</td>
                    <td style="font-weight:bold; ${r.status === 'Yapıldı' ? 'color:#166534;' : r.status === 'Beklemede' ? 'color:#92400e;' : 'color:#1e40af;'}">${r.status}</td>
                    <td>${r.resultReason || '—'}</td>
                </tr>
            `).join('');

            const excelTemplate = `
                <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
                <head>
                    <meta charset="utf-8">
                    <!--[if gte mso 9]>
                    <xml>
                        <x:ExcelWorkbook>
                            <x:ExcelWorksheets>
                                <x:ExcelWorksheet>
                                    <x:Name>Toplanti_Kararlari</x:Name>
                                    <x:WorksheetOptions>
                                        <x:DisplayGridlines/>
                                    </x:WorksheetOptions>
                                </x:ExcelWorksheet>
                            </x:ExcelWorksheets>
                        </x:ExcelWorkbook>
                    </xml>
                    <![endif]-->
                    <style>
                        table { border-collapse: collapse; width: 100%; }
                        th { background-color: #2563eb; color: #ffffff; font-weight: bold; border: 1px solid #1d4ed8; padding: 8px; text-align: left; }
                        td { border: 1px solid #cbd5e1; padding: 6px; font-size: 10pt; }
                        .title-row { font-size: 14pt; font-weight: bold; color: #1e3a8a; }
                    </style>
                </head>
                <body>
                    <table>
                        <tr>
                            <td colspan="11" class="title-row">MarketYönetimi360 — ${title}</td>
                        </tr>
                        <tr>
                            <td colspan="11"><b>Rapor Tarihi:</b> ${todayStr} | <b>Kayıt Adedi:</b> ${records.length} | <b>Kriterler:</b> ${data.filterInfo || 'Tümü'}</td>
                        </tr>
                        <tr></tr>
                        <thead>
                            <tr>
                                <th style="width:40px; text-align:center;">#</th>
                                <th>Kaynak Modül</th>
                                <th>Toplantı Dönemi</th>
                                <th>Toplantı Tarihi</th>
                                <th>Birim</th>
                                <th>Aksiyon / Karar</th>
                                <th>Sorumlu Kişi</th>
                                <th>Başlangıç Tarihi</th>
                                <th>Bitiş Tarihi</th>
                                <th>Durum</th>
                                <th>Sonuç / Gerekçe</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                </body>
                </html>
            `;

            const blob = new Blob(['\\ufeff' + excelTemplate], {
                type: 'application/vnd.ms-excel;charset=utf-8;'
            });

            const cleanFileName = `${title.replace(/[\\s\\/—]+/g, '_')}_${todayStr}.xls`;
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = cleanFileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);

            showToast(`${cleanFileName} Excel formatında başarıyla indirildi!`, "success");
        }
"""

# Find the entire chunk from where getScopedDecisions starts down to renderActionDecisionTable
# Let's use regex to replace all export functions before getRemainingDaysBadge / renderActionDecisionTable
html = re.sub(
    r'// =========================================================================\s*// 🆕 KARARLARI PDF.*?function exportDecisionsToExcel\(scope, customTitle\) \{.*?showToast\(`\$\{cleanFileName\} Excel formatında başarıyla indirildi!`, "success"\);\s*\}',
    clean_export_engine.strip(),
    html,
    flags=re.DOTALL
)

# Also remove any duplicate getScopedDecisions / exportDecisionsToPDF further down the file
html = re.sub(
    r'// =========================================================================\s*// 🆕 KARARLARI PDF VE WORD.*?function exportDecisionsToWord\(scope, customTitle\) \{.*?showToast\(`\$\{fileName\} Word formatında başarıyla indirildi!`, "success"\);\s*\}',
    '',
    html,
    flags=re.DOTALL
)
html = re.sub(
    r'// =========================================================================\s*// 🆕 KARARLARI PDF VE WORD.*?function exportDecisionsToWord\(scope, customTitle\) \{.*?showToast\(`\$\{cleanFileName\} \(\$\{records\.length\} filtrelenmiş kayıt\) Word formatında başarıyla indirildi!`, "success"\);\s*\}',
    '',
    html,
    flags=re.DOTALL
)

with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Duplicate export functions cleaned up and replaced!")
