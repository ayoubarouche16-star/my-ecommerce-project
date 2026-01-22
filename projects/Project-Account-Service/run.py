import os
from app import create_app, db

# =========================
# إعدادات التطبيق
# =========================
# التحقق من وجود CONFIG_OBJECT، وإضافة رابط قاعدة البيانات إذا لم يكن محددًا
config_object = os.environ.get("CONFIG_OBJECT", "app.config")

# يمكن تعريف رابط قاعدة بيانات SQLite افتراضي إذا لم يكن موجودًا في config
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")

app = create_app(config_object)

# =========================
# ربط قاعدة البيانات بالتطبيق (إجباري لـ Flask-SQLAlchemy)
# =========================
if not app.config.get("SQLALCHEMY_DATABASE_URI"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///app.db"
    )

app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

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

    print(f"🚀 تشغيل الـ Microservice على http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
