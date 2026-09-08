import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    is_dev = os.environ.get("ENV", "production").lower() == "development"
    print("==================================================================")
    print("  Smart Retail AI - Akıllı Yerel Market Yönetim Platformu")
    print(f"  Sunucu Başlatılıyor: http://0.0.0.0:{port}")
    print(f"  Swagger API Dokümantasyonu: http://0.0.0.0:{port}/docs")
    print("==================================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=is_dev)

