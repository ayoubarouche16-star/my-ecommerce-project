from flask import Blueprint, jsonify, request, current_app
from app.routes.decorators import login_required
from flask_login import current_user
import jwt
import datetime

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# مثال بيانات Dashboard
dashboard_data = {
    "balance": 1000.0,
    "recent_transactions": [
        {"id": 1, "amount": 100, "type": "credit"},
        {"id": 2, "amount": 50, "type": "debit"},
    ]
}

def jwt_required(func):
    """
    Decorator إضافي للتحقق من JWT في Header Authorization
    يعمل جنبًا إلى جنب مع Flask-Login
    """
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "JWT token مفقود"}), 401

        try:
            data = jwt.decode(token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"])
            user_id = data.get("user_id")
            # ✅ هنا يمكن إضافة تحقق إضافي إذا أردنا
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "JWT انتهت صلاحيته"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "JWT غير صالحة"}), 401

        return func(*args, **kwargs)
    return wrapper

@dashboard_bp.route("/", methods=["GET"])
@login_required
@jwt_required
def dashboard_home():
    try:
        return jsonify({"dashboard": dashboard_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# صفحة رئيسية مباشرة على /
# =========================
@dashboard_bp.route("/main-home", methods=["GET"])
@login_required
@jwt_required
def main_home():
    """
    روت للصفحة الرئيسية يمكن توجيه / إليه
    """
    try:
        return jsonify({
            "message": "مرحبًا بك في الصفحة الرئيسية!",
            "dashboard": dashboard_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
