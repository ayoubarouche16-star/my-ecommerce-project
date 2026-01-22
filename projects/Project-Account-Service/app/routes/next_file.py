# app/routes/next_file.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

next_file_bp = Blueprint("next_file", __name__, url_prefix="/next_file")

# =========================
# بيانات افتراضية كمثال
# =========================
user_data = {}

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "notes": [],
            "last_update": datetime.utcnow().isoformat()
        }
    return user_data[user_id]

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

# =========================
# Route: عرض الملاحظات
# =========================
@next_file_bp.route("/", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def get_notes():
    """عرض ملاحظات المستخدم"""
    data = get_user_data(current_user.id)

    # دعم التصفية حسب نص البحث
    search_query = request.args.get("search", "").strip()
    notes = data["notes"]
    if search_query:
        notes = [n for n in notes if search_query.lower() in n["note"].lower()]

    # ترتيب الملاحظات حسب التاريخ الأحدث أولاً
    notes = sorted(notes, key=lambda n: n.get("updated_at", n["created_at"]), reverse=True)

    return jsonify({"notes": notes, "last_update": data["last_update"], "total_notes": len(notes)}), 200

# =========================
# Route: إضافة ملاحظة جديدة
# =========================
@next_file_bp.route("/add", methods=["POST"])
@login_required
@roles_required("user", "admin", "vip")
def add_note():
    """إضافة ملاحظة جديدة للمستخدم"""
    data = request.get_json()
    note = data.get("note", "").strip()
    if not note:
        return jsonify({"error": "الملاحظة فارغة"}), 400

    user_notes = get_user_data(current_user.id)
    new_note = {
        "note": note,
        "created_at": datetime.utcnow().isoformat()
    }
    user_notes["notes"].append(new_note)
    user_notes["last_update"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تمت إضافة الملاحظة بنجاح", "notes": user_notes["notes"], "total_notes": len(user_notes["notes"])}), 201

# =========================
# Route: تعديل ملاحظة موجودة
# =========================
@next_file_bp.route("/edit/<int:note_index>", methods=["PUT"])
@login_required
@roles_required("user", "admin", "vip")
def edit_note(note_index):
    """تعديل ملاحظة موجودة"""
    data = request.get_json()
    new_note = data.get("note", "").strip()
    if not new_note:
        return jsonify({"error": "الملاحظة الجديدة فارغة"}), 400

    user_notes = get_user_data(current_user.id)
    if note_index < 0 or note_index >= len(user_notes["notes"]):
        return jsonify({"error": "الملاحظة غير موجودة"}), 404

    user_notes["notes"][note_index]["note"] = new_note
    user_notes["notes"][note_index]["updated_at"] = datetime.utcnow().isoformat()
    user_notes["last_update"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تم تعديل الملاحظة بنجاح", "notes": user_notes["notes"], "total_notes": len(user_notes["notes"])}), 200

# =========================
# Route: حذف ملاحظة
# =========================
@next_file_bp.route("/delete/<int:note_index>", methods=["DELETE"])
@login_required
@roles_required("user", "admin", "vip")
def delete_note(note_index):
    """حذف ملاحظة موجودة"""
    user_notes = get_user_data(current_user.id)
    if note_index < 0 or note_index >= len(user_notes["notes"]):
        return jsonify({"error": "الملاحظة غير موجودة"}), 404

    removed_note = user_notes["notes"].pop(note_index)
    user_notes["last_update"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تم حذف الملاحظة بنجاح", "removed_note": removed_note, "notes": user_notes["notes"], "total_notes": len(user_notes["notes"])}), 200

# =========================
# Route: إحصائيات الملاحظات
# =========================
@next_file_bp.route("/stats", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def notes_stats():
    """عرض إحصائيات الملاحظات لكل مستخدم"""
    data = get_user_data(current_user.id)
    total_notes = len(data["notes"])
    last_update = data["last_update"]
    latest_note = data["notes"][-1] if data["notes"] else None

    return jsonify({
        "total_notes": total_notes,
        "last_update": last_update,
        "latest_note": latest_note
    }), 200
