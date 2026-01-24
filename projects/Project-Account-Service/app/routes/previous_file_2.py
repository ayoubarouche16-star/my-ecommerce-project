# app/routes/previous_file_2.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

previous_file_2_bp = Blueprint("previous_file_2", __name__, url_prefix="/previous_file_2")

# =========================
# بيانات افتراضية
# =========================
user_logs = {}

def get_user_logs(user_id):
    if user_id not in user_logs:
        user_logs[user_id] = []
    return user_logs[user_id]

# =========================
# Decorator للتحكم في الوصول حسب دور المستخدم
# =========================
def roles_required(*allowed_roles):
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
# Route: عرض جميع السجلات
# =========================
@previous_file_2_bp.route("/", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def list_logs():
    """عرض جميع السجلات للمستخدم"""
    logs = get_user_logs(current_user.id)
    # يمكن إضافة فرز حسب التاريخ أو غيره مستقبلاً
    return jsonify({"logs": logs, "last_update": datetime.utcnow().isoformat()}), 200

# =========================
# Route: إضافة سجل جديد
# =========================
@previous_file_2_bp.route("/add", methods=["POST"])
@login_required
@roles_required("user", "admin", "vip")
def add_log():
    """إضافة سجل جديد"""
    data = request.get_json()
    log_entry = data.get("log", "").strip()
    if not log_entry:
        return jsonify({"error": "السجل فارغ"}), 400

    logs = get_user_logs(current_user.id)
    logs.append({
        "log": log_entry,
        "created_at": datetime.utcnow().isoformat()
    })

    return jsonify({"message": "تم إضافة السجل بنجاح", "logs": logs}), 201

# =========================
# Route: تعديل سجل موجود
# =========================
@previous_file_2_bp.route("/edit/<int:log_index>", methods=["PUT"])
@login_required
@roles_required("user", "admin", "vip")
def edit_log(log_index):
    """تعديل سجل موجود"""
    data = request.get_json()
    new_log = data.get("log", "").strip()
    if not new_log:
        return jsonify({"error": "السجل الجديد فارغ"}), 400

    logs = get_user_logs(current_user.id)
    if log_index < 0 or log_index >= len(logs):
        return jsonify({"error": "السجل غير موجود"}), 404

    logs[log_index]["log"] = new_log
    logs[log_index]["updated_at"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تم تعديل السجل بنجاح", "logs": logs}), 200

# =========================
# Route: حذف سجل موجود
# =========================
@previous_file_2_bp.route("/delete/<int:log_index>", methods=["DELETE"])
@login_required
@roles_required("user", "admin", "vip")
def delete_log(log_index):
    """حذف سجل موجود"""
    logs = get_user_logs(current_user.id)
    if log_index < 0 or log_index >= len(logs):
        return jsonify({"error": "السجل غير موجود"}), 404

    removed_log = logs.pop(log_index)
    return jsonify({"message": "تم حذف السجل بنجاح", "removed_log": removed_log, "logs": logs}), 200
