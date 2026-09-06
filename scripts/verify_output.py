# -*- coding: utf-8 -*-
import urllib.request

url = "http://127.0.0.1:8000/"
try:
    req = urllib.request.urlopen(url)
    content = req.read().decode('utf-8')
    print("HTTP Status:", req.status)
    checks = [
        "Toplantılar Karar Özeti",
        "İcra Kurulu Toplantısı",
        "Satınalma & Kategori Toplantıları",
        "Saha & Satış Değerlendirme",
        "Finans Yönetimi",
        "İnsan Kaynakları",
        "Teknik Bakım",
        "Bilgi Teknolojileri",
        "Yatırım ve Yeni Mağaza",
        "Pazarlama & Marka",
        "Müşteri Deneyimi",
        "Kâr-Zarar (P&L) Konsolidasyonu",
        "Eğitim & Sertifikasyon Takibi",
        "Ruhsat & Resmi İzin Takibi",
        "İş Kazası Kayıt Defteri",
        "Şube Kapanış/Devir Değerlendirmesi",
        "Envanter Sayım Farkı Analizi",
        "actionDecisionStore",
        "summaryRoleSimulator"
    ]
    for check in checks:
        found = check in content
        print(f"[{'OK' if found else 'FAIL'}] Check '{check}': {found}")
except Exception as e:
    print("Error connecting to server:", e)
