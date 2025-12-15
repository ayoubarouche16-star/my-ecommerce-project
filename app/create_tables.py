# create_tables.py
# يشغّل هذا الملف لإنشاء جميع الجداول المعرفة بواسطة Base.metadata.create_all
from app.database.db import engine, Base
# استيراد النماذج حتى يتم تسجيلها في Base
# (يستورد وحدات النماذج حتى يتم تعريفها، لا حاجة للاستخدام المباشر هنا)
import app.models.user  # إضافة import لكل ملف نموذج جديد لاحقًا

def create_all():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created (if not existed).")

if __name__ == "__main__":
    create_all()
from app.database.db import create_tables

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully ✅")
