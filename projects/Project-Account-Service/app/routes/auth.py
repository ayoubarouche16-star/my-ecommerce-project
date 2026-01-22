from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
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

    # ✅ إضافة مطلوبة لـ Flask-Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False


SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # محفوظ كما هو (لن نكسره)

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


# تسجيل الدخول مع إنشاء JWT + Flask-Login
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)
        username = data.get("username")
        password = data.get("password")

        user = users_db.get(username)
        if not user or not user.check_password(password):
            return jsonify({"error": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

        # ✅ تسجيل الدخول عبر Flask-Login
        login_user(user)

        # إنشاء التوكن مع صلاحية 24 ساعة
        token = jwt.encode(
            {
                "user_id": user.get_id(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            current_app.config.get("SECRET_KEY", SECRET_KEY),
            algorithm="HS256"
        )

        return jsonify({
            "message": "تم تسجيل الدخول بنجاح",
            "user_id": user.get_id(),
            "token": token
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# تسجيل الخروج
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "تم تسجيل الخروج بنجاح"}), 200


# حالة المستخدم
@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"message": "المستخدم مسجّل دخول"}), 200
