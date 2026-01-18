# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# =========================
# Extensions
# =========================
db = SQLAlchemy()
login_manager = LoginManager()

# =========================
# Factory Function
# =========================
def create_app(config_object="app.config.Config"):
    """
    إنشاء تطبيق Flask باستخدام Factory Pattern
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # =========================
    # تهيئة الإضافات
    # =========================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # =========================
    # تسجيل Blueprints
    # =========================
    from app.routes.accounts import accounts_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transfer import transfer_bp

    app.register_blueprint(accounts_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transfer_bp)

    # =========================
    # تهيئة قاعدة البيانات
    # =========================
    with app.app_context():
        db.create_all()
        print("✅ قاعدة البيانات جاهزة!")

    return app

# =========================
# User Loader لـ Flask-Login
# =========================
from app.routes.auth import users_db, User

@login_manager.user_loader
def load_user(user_id):
    """
    تحميل المستخدم بناءً على user_id
    """
    for user in users_db.values():
        if user.get_id() == str(user_id):
            return user
    return None
