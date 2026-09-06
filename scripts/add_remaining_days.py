# -*- coding: utf-8 -*-
"""
Adds remaining days calculation and visual badge to Action/Decision tables in dashboard.html
"""
import re

SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Define getRemainingDaysBadge function in JS
js_func = """
        // Bitiş tarihine kalan gün hesaplayıcı & dinamik rozet
        function getRemainingDaysBadge(endDateStr, status) {
            if (!endDateStr || endDateStr === '—') return '';
            // Sistem referans tarihi (veya anlık tarih)
            const today = new Date('2026-09-06');
            const target = new Date(endDateStr);
            const diffTime = target - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (status === 'Yapıldı') {
                return `<span class="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200 mt-1 shadow-2xs"><i class="fa-solid fa-check text-[9px]"></i> Tamamlandı</span>`;
            }

            if (diffDays < 0) {
                return `<span class="inline-flex items-center gap-1 text-[10px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200 animate-pulse mt-1 shadow-2xs"><i class="fa-solid fa-triangle-exclamation text-[9px]"></i> ${Math.abs(diffDays)} gün gecikti</span>`;
            } else if (diffDays === 0) {
                return `<span class="inline-flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-300 mt-1 shadow-2xs"><i class="fa-solid fa-bell text-[9px] animate-bounce"></i> Bugün son gün</span>`;
            } else if (diffDays <= 3) {
                return `<span class="inline-flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-300 mt-1 shadow-2xs"><i class="fa-solid fa-hourglass-half text-[9px]"></i> ${diffDays} gün kaldı</span>`;
            } else {
                return `<span class="inline-flex items-center gap-1 text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200 mt-1 shadow-2xs"><i class="fa-regular fa-clock text-[9px]"></i> ${diffDays} gün kaldı</span>`;
            }
        }
"""

if 'function getRemainingDaysBadge' not in html:
    # Insert right before renderActionDecisionTable
    target_pos = html.find('function renderActionDecisionTable')
    if target_pos != -1:
        html = html[:target_pos] + js_func + "\n        " + html[target_pos:]
        print("getRemainingDaysBadge added to JS!")

# 2. Update renderActionDecisionTable to include remaining days
old_td = """<td class="p-3 whitespace-nowrap text-slate-500 text-[11px]">${r.startDate} &rarr; <span class="font-bold text-slate-700">${r.endDate}</span></td>"""
new_td = """<td class="p-3 whitespace-nowrap text-slate-500 text-[11px]">
                            <div>${r.startDate} &rarr; <span class="font-bold text-slate-700">${r.endDate}</span></div>
                            <div>${getRemainingDaysBadge(r.endDate, r.status)}</div>
                        </td>"""

if old_td in html:
    html = html.replace(old_td, new_td)
    print("renderActionDecisionTable Süre column updated!")
else:
    print("Warning: old_td in renderActionDecisionTable not matched, trying regex")
    html = re.sub(r'<td class="p-3 whitespace-nowrap text-slate-500 text-\[11px\]">\$\{r\.startDate\} &rarr; <span class="font-bold text-slate-700">\$\{r\.endDate\}</span></td>', new_td, html)

# 3. Update filterMeetingsSummary (Toplantılar Karar Özeti) to include remaining days in Bitiş column
old_sum_td = """<td class="p-3 whitespace-nowrap font-bold text-slate-700">${r.endDate}</td>"""
new_sum_td = """<td class="p-3 whitespace-nowrap">
                        <div class="font-bold text-slate-700">${r.endDate}</div>
                        <div>${getRemainingDaysBadge(r.endDate, r.status)}</div>
                    </td>"""

if old_sum_td in html:
    html = html.replace(old_sum_td, new_sum_td)
    print("filterMeetingsSummary Bitiş column updated!")
else:
    print("Warning: old_sum_td not matched, trying regex")
    html = re.sub(r'<td class="p-3 whitespace-nowrap font-bold text-slate-700">\$\{r\.endDate\}</td>', new_sum_td, html)

with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("All remaining days indicators successfully added!")
