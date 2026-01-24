# app/routes/next_file_2.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

next_file_2_bp = Blueprint("next_file_2", __name__, url_prefix="/next_file_2")

# بيانات افتراضية
user_tasks = {}

def get_user_tasks(user_id):
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    return user_tasks[user_id]

# =========================
# Decorator للتحكم في الصلاحيات
# =========================
def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(current_user, "role", "user")
            if user_role not in allowed_roles:
                return jsonify({"error": "غير مصرح لك"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@next_file_2_bp.route("/", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def list_tasks():
    """عرض جميع مهام المستخدم"""
    tasks = get_user_tasks(current_user.id)
    return jsonify({"tasks": tasks, "last_update": datetime.utcnow().isoformat()}), 200

@next_file_2_bp.route("/add", methods=["POST"])
@login_required
@roles_required("user", "admin", "vip")
def add_task():
    """إضافة مهمة جديدة"""
    data = request.get_json()
    task = data.get("task", "").strip()
    priority = data.get("priority", "normal")

    if not task:
        return jsonify({"error": "المهمة فارغة"}), 400

    tasks = get_user_tasks(current_user.id)
    tasks.append({
        "task": task,
        "status": "pending",
        "priority": priority,
        "created_at": datetime.utcnow().isoformat()
    })

    return jsonify({"message": "تمت إضافة المهمة بنجاح", "tasks": tasks}), 201

# =========================
# تعديل مهمة
# =========================
@next_file_2_bp.route("/edit/<int:task_index>", methods=["PUT"])
@login_required
@roles_required("user", "admin", "vip")
def edit_task(task_index):
    data = request.get_json()
    tasks = get_user_tasks(current_user.id)

    if task_index < 0 or task_index >= len(tasks):
        return jsonify({"error": "المهمة غير موجودة"}), 404

    tasks[task_index]["task"] = data.get("task", tasks[task_index]["task"])
    tasks[task_index]["priority"] = data.get("priority", tasks[task_index].get("priority", "normal"))
    tasks[task_index]["updated_at"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تم تعديل المهمة", "tasks": tasks}), 200

# =========================
# تغيير حالة المهمة
# =========================
@next_file_2_bp.route("/status/<int:task_index>", methods=["PATCH"])
@login_required
@roles_required("user", "admin", "vip")
def change_status(task_index):
    data = request.get_json()
    status = data.get("status", "pending")

    tasks = get_user_tasks(current_user.id)
    if task_index < 0 or task_index >= len(tasks):
        return jsonify({"error": "المهمة غير موجودة"}), 404

    tasks[task_index]["status"] = status
    tasks[task_index]["updated_at"] = datetime.utcnow().isoformat()

    return jsonify({"message": "تم تحديث حالة المهمة", "tasks": tasks}), 200

# =========================
# حذف مهمة
# =========================
@next_file_2_bp.route("/delete/<int:task_index>", methods=["DELETE"])
@login_required
@roles_required("user", "admin", "vip")
def delete_task(task_index):
    tasks = get_user_tasks(current_user.id)

    if task_index < 0 or task_index >= len(tasks):
        return jsonify({"error": "المهمة غير موجودة"}), 404

    removed = tasks.pop(task_index)
    return jsonify({"message": "تم حذف المهمة", "removed_task": removed, "tasks": tasks}), 200

# =========================
# إحصائيات المهام
# =========================
@next_file_2_bp.route("/stats", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def tasks_stats():
    tasks = get_user_tasks(current_user.id)

    stats = {
        "total": len(tasks),
        "completed": len([t for t in tasks if t.get("status") == "completed"]),
        "pending": len([t for t in tasks if t.get("status") == "pending"]),
        "high_priority": len([t for t in tasks if t.get("priority") == "high"])
    }

    return jsonify({"stats": stats, "generated_at": datetime.utcnow().isoformat()}), 200
