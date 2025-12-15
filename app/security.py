# app/security.py
from functools import wraps
from flask import session, redirect, url_for, flash
import time

# ------------------------
# حماية الدخول
# ------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("يجب تسجيل الدخول للوصول إلى هذه الصفحة", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------
# حماية الأدمن
# ------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("هذه الصفحة خاصة بالأدمن فقط", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------
# تحديد عدد المحاولات لكل إجراء (Rate Limit)
# ------------------------
USER_ACTIONS = {}

def rate_limit(max_attempts=5, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            now = time.time()
            if user_id:
                attempts = USER_ACTIONS.get(user_id, [])
                # إزالة المحاولات القديمة
                attempts = [t for t in attempts if now - t < window_seconds]
                if len(attempts) >= max_attempts:
                    flash("تم تجاوز الحد المسموح من العمليات، حاول لاحقًا", "warning")
                    return redirect(url_for("dashboard"))
                attempts.append(now)
                USER_ACTIONS[user_id] = attempts
            return f(*args, **kwargs)
        return decorated_function
    return decorator
