import uvicorn

if __name__ == "__main__":
    print("==================================================================")
    print("  Smart Retail AI - Akıllı Yerel Market Yönetim Platformu")
    print("  Sunucu Başlatılıyor: http://127.0.0.1:8000")
    print("  Swagger API Dokümantasyonu: http://127.0.0.1:8000/docs")
    print("==================================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
