# app/routes/fourteenth_file.py

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

fourteenth_file_bp = Blueprint("fourteenth_file", __name__, url_prefix="/fourteenth_file")

# =========================
# بيانات افتراضية للإشعارات
# =========================
user_notifications = {}

def get_notifications(user_id):
    if user_id not in user_notifications:
        user_notifications[user_id] = []
    return user_notifications[user_id]

# =========================
# Decorator للتحكم في الوصول حسب نوع المستخدم
# =========================
def roles_required(*allowed_roles):
    """
    تحقق من أن المستخدم الحالي يمتلك أحد الأدوار المسموح بها
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(current_user, "role", "user")  # افتراضي: user
            if user_role not in allowed_roles:
                return jsonify({"error": "غير مصرح لك بالوصول إلى هذه الصفحة"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =========================
# Routes للإشعارات (موجودة مسبقًا)
# =========================
@fourteenth_file_bp.route("/", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def list_notifications():
    """عرض جميع الإشعارات للمستخدم"""
    notifications = get_notifications(getattr(current_user, "id", None))
    return jsonify({"notifications": notifications, "last_update": datetime.utcnow().isoformat()}), 200

@fourteenth_file_bp.route("/add", methods=["POST"])
@login_required
@roles_required("admin", "vip")
def add_notification():
    """إضافة إشعار جديد"""
    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "رسالة الإشعار فارغة"}), 400

    notifications = get_notifications(getattr(current_user, "id", None))
    notifications.append({"message": message, "created_at": datetime.utcnow().isoformat()})

    return jsonify({"message": "تمت إضافة الإشعار بنجاح", "notifications": notifications}), 201

# =========================
# بيانات الموقع العامة
# =========================
site_header = {
    "logo": "Deeb.Weep.54.DRS",
    "official_partner": "الجزائر 🇩🇿",
    "languages": ["ar", "en", "fr"],
    "links": {
        "login": "/auth/login",
        "register": "/auth/register"
    }
}

site_sections = {
    "main_navigation": ["التداول", "المواصفات", "خصائص فريدة", "تعلم", "تحليل السوق", "الشركاء"],
    "homepage": {
        "cta": "ابدأ التداول اليوم",
        "cta_secondary": "جرب الحساب التجريبي",
        "highlights": [
            "فروق أسعار ثابتة",
            "حماية من الرصيد السلبي",
            "وقف الخسارة المضمون"
        ]
    },
    "features": {
        "trading": ["الأسواق", "طرق التداول", "أنواع الحسابات", "حساب محترف", "الحزم المميزة"],
        "specifications": ["منصات التداول", "تطبيق الجوال", "TradingView", "MT4", "MT5"],
        "unique_features": ["أدوات التداول", "شروط التداول"],
        "learning": ["كتب إلكترونية", "مقالات", "مقاطع فيديو", "معجم التداول", "مؤشرات اقتصادية"],
        "market_analysis": ["أسعار العملات", "التقويم المالي", "أدوات التحليل", "منصات التداول"]
    },
    "future_features": ["محفظة رقمية متقدمة", "دعم عملات مشفرة إضافية", "دمج AI للتحليلات", "لوحة تحكم تفصيلية VIP", "تنبيهات وإشعارات"]
}

# =========================
# Route لبيانات الموقع العامة
# =========================
@fourteenth_file_bp.route("/site-info", methods=["GET"])
def site_info():
    """عرض بيانات الموقع العامة وواجهة المستخدم"""
    return jsonify({
        "header": site_header,
        "sections": site_sections
    }), 200
