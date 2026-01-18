# run.py

import os
from app import create_app, db

# =========================
# إعدادات التطبيق
# =========================
config_object = os.environ.get("CONFIG_OBJECT", "app.config.Config")
app = create_app(config_object)

# =========================
# إنشاء قاعدة البيانات إذا لم تكن موجودة
# =========================
with app.app_context():
    db.create_all()
    print("✅ قاعدة البيانات جاهزة!")

# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = app.config.get("DEBUG", True)

    print(f"🚀 تشغيل الـ Microservice على http://{host}:{port} (Debug={debug})")
    app.run(host=host, port=port, debug=debug)
