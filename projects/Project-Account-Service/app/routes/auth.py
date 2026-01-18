from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# قاعدة بيانات افتراضية للمستخدمين
users_db = {}

class User:
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # ضع مفتاح سري قوي هنا

# تسجيل مستخدم جديد
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "الاسم وكلمة المرور مطلوبان"}), 400

        if username in users_db:
            return jsonify({"error": "المستخدم موجود بالفعل"}), 400

        user_id = len(users_db) + 1
        password_hash = generate_password_hash(password)
        user = User(user_id, username, password_hash)
        users_db[username] = user

        return jsonify({"message": "تم إنشاء الحساب بنجاح", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# تسجيل الدخول مع إنشاء JWT
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)
        username = data.get("username")
        password = data.get("password")

        user = users_db.get(username)
        if not user or not user.check_password(password):
            return jsonify({"error": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

        # إنشاء التوكن مع صلاحية 24 ساعة
        token = jwt.encode({
            "user_id": user.get_id(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({"message": "تم تسجيل الدخول بنجاح", "user_id": user.get_id(), "token": token}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# تسجيل الخروج
@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "تم تسجيل الخروج بنجاح"}), 200

# حالة المستخدم
@auth_bp.route("/me", methods=["GET"])
def me():
    user_demo = {"id": 1, "username": "demo"}
    return jsonify({"user": user_demo}), 200
