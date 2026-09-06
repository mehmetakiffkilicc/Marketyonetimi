# -*- coding: utf-8 -*-
"""
Updates filterMeetingsSummary to dynamically change the table header title when unit/source is selected.
"""
SOURCE_HTML = r"app/templates/dashboard.html"

with open(SOURCE_HTML, "r", encoding="utf-8") as f:
    html = f.read()

old_badge_part = """            // Count badge
            const badge = document.getElementById('summaryCountBadge');
            if (badge) badge.innerText = `${filtered.length} Kayıt Gösteriliyor`;"""

new_badge_part = """            // Count badge & Dinamik Başlık Güncelleme
            const badge = document.getElementById('summaryCountBadge');
            if (badge) badge.innerText = `${filtered.length} Kayıt`;

            const tableHeaderTitle = document.getElementById('summaryTableHeaderTitle');
            if (tableHeaderTitle) {
                if (unit) {
                    tableHeaderTitle.innerText = `${unit} Birimi — Toplantı Karar Özeti`;
                } else if (source) {
                    tableHeaderTitle.innerText = `${source} — Karar Özeti`;
                } else {
                    tableHeaderTitle.innerText = `Konsolide Karar ve Aksiyon Kayıtları`;
                }
            }"""

if old_badge_part in html:
    html = html.replace(old_badge_part, new_badge_part)
    print("filterMeetingsSummary updated with dynamic title change!")

with open(SOURCE_HTML, "w", encoding="utf-8") as f:
    f.write(html)
