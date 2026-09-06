# -*- coding: utf-8 -*-
"""
Updates PDF & Word export logic in dashboard.html so that:
- It exports ONLY the filtered records when filters/search/roles are applied
- It prints the active filters summary in the PDF and Word header metadata
- It handles empty filtered sets cleanly with feedback
"""
import re

SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update getScopedDecisions and export functions in JS
new_export_js = """
        // =========================================================================
        // 🆕 KARARLARI PDF VE WORD DÖKÜMANI OLARAK DIŞA AKTARMA (EXPORT) MOTORU
        // (Filtrelenen kayıtları dinamik olarak yakalar ve aktarır)
        // =========================================================================
        let currentFilteredSummaryRecords = null;

        function getScopedDecisions(scope) {
            if (scope === 'icra') {
                const recs = actionDecisionStore.filter(r => r.sourceModule === 'İcra Kurulu Toplantısı' && r.period === currentIcraQuarter);
                return {
                    title: `İcra Kurulu Toplantı Kararları (${currentIcraQuarter})`,
                    period: currentIcraQuarter,
                    filterInfo: `Dönem: ${currentIcraQuarter}`,
                    records: recs
                };
            } else if (scope === 'purchasing') {
                const p = `${currentPurchasingMonth} - ${currentPurchasingWeek}`;
                const recs = actionDecisionStore.filter(r => r.sourceModule === 'Satınalma & Kategori Toplantısı' && (r.period === p || r.period.includes(currentPurchasingMonth)));
                return {
                    title: `Satınalma & Kategori Toplantı Kararları (${p})`,
                    period: p,
                    filterInfo: `Ay: ${currentPurchasingMonth}, Hafta: ${currentPurchasingWeek}`,
                    records: recs
                };
            } else if (scope === 'field') {
                const p = `${currentFieldMonth} - ${currentFieldWeek}`;
                const recs = actionDecisionStore.filter(r => r.sourceModule === 'Saha & Satış Değerlendirme' && (r.period === p || r.period.includes(currentFieldMonth)));
                return {
                    title: `Saha & Satış Değerlendirme Kararları (${p})`,
                    period: p,
                    filterInfo: `Ay: ${currentFieldMonth}, Hafta: ${currentFieldWeek}`,
                    records: recs
                };
            } else if (scope === 'tracking') {
                const recs = actionDecisionStore.filter(r => r.sourceModule.includes('Toplantı') || r.sourceModule.includes('İcra') || r.sourceModule.includes('Saha'));
                return {
                    title: `Toplantı Karar Takip Çizelgesi`,
                    period: 'Tüm Dönemler',
                    filterInfo: 'Filtre: Toplantı Kararları',
                    records: recs
                };
            } else {
                // 'summary' - Dinamik Filtrelenmiş Liste
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
                if (source) filterDescriptions.push(`Kaynak: ${source}`);
                if (unit) filterDescriptions.push(`Birim: ${unit}`);
                if (status) filterDescriptions.push(`Durum: ${status}`);
                if (period) filterDescriptions.push(`Dönem: ${period}`);
                if (assignee) filterDescriptions.push(`Sorumlu: ${assignee}`);
                if (search) filterDescriptions.push(`Arama: "${search}"`);

                let filtered = actionDecisionStore.filter(r => {
                    // Rol filtreleme
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

                    // Kriter filtreleme
                    if (source && r.sourceModule !== source) return false;
                    if (unit && r.unit !== unit) return false;
                    if (status && r.status !== status) return false;
                    if (period && r.period !== period && !r.period.includes(period)) return false;
                    if (assignee && r.assignee !== assignee) return false;
                    if (search && !r.actionDecision.toLowerCase().includes(search) && !r.resultReason.toLowerCase().includes(search)) return false;

                    return true;
                });

                return {
                    title: `Konsolide Toplantılar Karar Özeti Raporu`,
                    period: period || 'Tüm Dönemler',
                    filterInfo: filterDescriptions.join(' | '),
                    records: filtered
                };
            }
        }

        // 1. PDF Olarak İndir / Yazdır (Filtrelenen kısmı döker)
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

                    ${data.filterInfo ? `<div class="filter-badge-box"><b>🔍 Uygulanan Filtre Kriterleri:</b> ${data.filterInfo}</div>` : ''}

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
            showToast(`${title} (${records.length} filtrelenmiş kayıt) PDF formatında hazırlandı.`, "success");
        }

        // 2. Word (.doc) Olarak İndir (Filtrelenen kısmı döker)
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

            const cleanFileName = `${title.replace(/[\\s\\/]+/g, '_')}_Filtreli_${todayStr}.doc`;
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = cleanFileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);

            showToast(`${cleanFileName} (${records.length} filtrelenmiş kayıt) Word formatında başarıyla indirildi!`, "success");
        }
"""

# Replace old export block in html
start_marker = "// =========================================================================" + "\n" + "        // 🆕 KARARLARI PDF VE WORD DÖKÜMANI OLARAK DIŞA AKTARMA (EXPORT) MOTORU"
end_marker = "        // Bitiş tarihine kalan gün hesaplayıcı"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + new_export_js + "\n\n" + html[end_idx:]
    print("Export functions updated with dynamic filtering support!")
else:
    print("Warning: markers not found, attempting regex replacement")
    html = re.sub(
        r'// =========================================================================\s*// 🆕 KARARLARI PDF VE WORD.*?function exportDecisionsToWord\(scope, customTitle\) \{.*?showToast\(`\$\{fileName\} Word formatında başarıyla indirildi!`, "success"\);\s*\}',
        new_export_js.strip(),
        html,
        flags=re.DOTALL
    )

with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Export filtering update complete!")
