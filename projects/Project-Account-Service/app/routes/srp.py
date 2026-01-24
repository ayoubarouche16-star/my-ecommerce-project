# app/routes/srp.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from app.models.user import User
from app.database.db import db
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from functools import wraps
import csv
import io
from flask_mail import Mail, Message

# =========================
# إنشاء Blueprint
# =========================
srp_bp = Blueprint('srp', __name__, template_folder='templates', url_prefix='/srp')

# =========================
# سجل الأنشطة
# =========================
activity_logs = {}

def log_activity(user_id, action):
    """تسجيل الأنشطة لكل مستخدم"""
    if user_id not in activity_logs:
        activity_logs[user_id] = []
    activity_logs[user_id].append({
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    })

# =========================
# التحقق من الصلاحيات
# =========================
def roles_required(*allowed_roles):
    """تأكد من أن المستخدم الحالي يمتلك أحد الأدوار المسموح بها"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(current_user, "role", "user")
            if user_role not in allowed_roles:
                flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('srp.srp_home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =========================
# إرسال إشعار بالبريد
# =========================
def send_email(subject, recipients, body):
    mail = Mail(current_app)
    msg = Message(subject, recipients=recipients, body=body)
    try:
        mail.send(msg)
    except Exception as e:
        print(f"❌ خطأ في إرسال البريد: {e}")

# =========================
# الصفحة الرئيسية SRP
# =========================
@srp_bp.route('/')
@login_required
@roles_required("admin", "vip")
def srp_home():
    """صفحة رئيسية مع قائمة المستخدمين"""
    users = User.query.all()
    return render_template('srp_home.html', users=users)

# =========================
# إضافة مستخدم
# =========================
@srp_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required("admin", "vip")
def add_user_srp():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        if not username or not email or not password:
            flash('جميع الحقول مطلوبة!', 'danger')
            return redirect(url_for('srp.add_user_srp'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        log_activity(current_user.id, f"تمت إضافة مستخدم جديد: {username}")
        flash('تمت إضافة المستخدم بنجاح!', 'success')

        # إرسال إشعار بالبريد
        send_email(
            subject="تمت إضافة مستخدم جديد",
            recipients=[current_user.email],
            body=f"تمت إضافة المستخدم {username} (Role: {role}) بواسطة {current_user.username}."
        )

        return redirect(url_for('srp.srp_home'))

    return render_template('add_user_srp.html')

# =========================
# تعديل مستخدم
# =========================
@srp_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required("admin", "vip")
def edit_user_srp(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', user.role)

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = generate_password_hash(password, method='sha256')
        user.role = role

        db.session.commit()
        log_activity(current_user.id, f"تم تعديل مستخدم: {user.username}")
        flash('تم تحديث بيانات المستخدم بنجاح!', 'success')

        # إرسال إشعار بالبريد
        send_email(
            subject="تم تعديل مستخدم",
            recipients=[current_user.email],
            body=f"تم تعديل المستخدم {user.username} بواسطة {current_user.username}."
        )

        return redirect(url_for('srp.srp_home'))

    return render_template('edit_user_srp.html', user=user)

# =========================
# حذف مستخدم
# =========================
@srp_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@roles_required("admin", "vip")
def delete_user_srp(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    log_activity(current_user.id, f"تم حذف مستخدم: {user.username}")
    flash('تم حذف المستخدم بنجاح!', 'success')

    # إرسال إشعار بالبريد
    send_email(
        subject="تم حذف مستخدم",
        recipients=[current_user.email],
        body=f"تم حذف المستخدم {user.username} بواسطة {current_user.username}."
    )

    return redirect(url_for('srp.srp_home'))

# =========================
# عرض سجلات الأنشطة
# =========================
@srp_bp.route('/logs/<int:user_id>')
@login_required
@roles_required("admin", "vip")
def view_activity_logs(user_id):
    logs = activity_logs.get(user_id, [])
    return jsonify({"user_id": user_id, "activity_logs": logs}), 200

# =========================
# تصدير سجل الأنشطة CSV
# =========================
@srp_bp.route('/logs/<int:user_id>/export')
@login_required
@roles_required("admin", "vip")
def export_activity_logs(user_id):
    logs = activity_logs.get(user_id, [])
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Action', 'Timestamp'])
    for log in logs:
        cw.writerow([log['action'], log['timestamp']])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'user_{user_id}_logs.csv')

# =========================
# البحث والتصفية المتقدمة
# =========================
@srp_bp.route('/search')
@login_required
@roles_required("admin", "vip")
def search_users():
    query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()
    if query:
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
        ).all()
    else:
        users = User.query.all()

    if role_filter:
        users = [u for u in users if u.role == role_filter]

    return render_template('srp_home.html', users=users)
