# app/__init__.py

import os
from flask import Flask, redirect, url_for
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
    # 🔐 SECRET KEY
    # =========================
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.environ.get(
            "SECRET_KEY",
            "dev-secret-key-change-me"
        )

    # =========================
    # 🔧 إعداد قاعدة البيانات
    # =========================
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///app.db"
        )

    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # =========================
    # تهيئة الإضافات
    # =========================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"

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
    # الصفحة الرئيسية
    # =========================
    @app.route("/", methods=["GET"])
    def root_redirect():
        return redirect(url_for("dashboard.main_home"))

    # =========================
    # إنشاء جداول قاعدة البيانات
    # =========================
    with app.app_context():
        db.create_all()
        print("✅ قاعدة البيانات جاهزة!")

    return app

# =========================
# User Loader
# =========================
from app.routes.auth import users_db, User

@login_manager.user_loader
def load_user(user_id):
    for user in users_db.values():
        if user.get_id() == str(user_id):
            return user
    return None
