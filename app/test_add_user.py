from app.database.db import SessionLocal, engine, Base
from app.models.user import User

# إنشاء جلسة
db = SessionLocal()

# إنشاء مستخدم جديد للاختبار
u = User(name="Test User", email="test@example.com")
u.set_password("secret123")

db.add(u)
db.commit()
print("User added with id:", u.id)

# جلب المستخدم والتحقق
found = db.query(User).filter(User.email == "test@example.com").first()
print("Found:", found.to_dict() if found else "Not found")
db.close()
