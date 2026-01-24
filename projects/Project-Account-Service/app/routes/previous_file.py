# app/routes/previous_file.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

previous_file_bp = Blueprint("previous_file", __name__, url_prefix="/previous_file")

# =========================
# بيانات افتراضية كمثال
# =========================
user_history = {}

def get_user_history(user_id):
    if user_id not in user_history:
        user_history[user_id] = []
    return user_history[user_id]

# =========================
# Decorator للتحكم في الوصول حسب نوع المستخدم
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

@previous_file_bp.route("/", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def view_history():
    """عرض تاريخ المستخدم"""
    history = get_user_history(current_user.id)
    return jsonify({"history": history, "last_update": datetime.utcnow().isoformat()}), 200

@previous_file_bp.route("/add", methods=["POST"])
@login_required
@roles_required("user", "admin", "vip")
def add_history_item():
    """إضافة عنصر جديد للتاريخ"""
    data = request.get_json()
    action = data.get("action", "").strip()
    if not action:
        return jsonify({"error": "العنصر فارغ"}), 400

    history = get_user_history(current_user.id)
    history.append({
        "action": action,
        "created_at": datetime.utcnow().isoformat()
    })

    return jsonify({"message": "تمت إضافة العنصر بنجاح", "history": history}), 201

@previous_file_bp.route("/edit/<int:item_index>", methods=["PUT"])
@login_required
@roles_required("user", "admin", "vip")
def edit_history_item(item_index):
    """تعديل عنصر موجود في التاريخ"""
    data = request.get_json()
    new_action = data.get("action", "").strip()
    if not new_action:
        return jsonify({"error": "العنصر الجديد فارغ"}), 400

    history = get_user_history(current_user.id)
    if item_index < 0 or item_index >= len(history):
        return jsonify({"error": "العنصر غير موجود"}), 404

    history[item_index]["action"] = new_action
    history[item_index]["updated_at"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تم تعديل العنصر بنجاح", "history": history}), 200

@previous_file_bp.route("/delete/<int:item_index>", methods=["DELETE"])
@login_required
@roles_required("user", "admin", "vip")
def delete_history_item(item_index):
    """حذف عنصر موجود في التاريخ"""
    history = get_user_history(current_user.id)
    if item_index < 0 or item_index >= len(history):
        return jsonify({"error": "العنصر غير موجود"}), 404

    removed_item = history.pop(item_index)

    return jsonify({"message": "تم حذف العنصر بنجاح", "removed_item": removed_item, "history": history}), 200
