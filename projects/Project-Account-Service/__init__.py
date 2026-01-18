from flask import Flask
from .extensions import db, migrate
from .routes import auth_bp, dashboard_bp, transfer_bp, accounts_bp

def create_app():
    """Factory Function لإنشاء التطبيق"""
    app = Flask(__name__)

    # إعدادات التطبيق
    app.config.from_object("app.config.Config")

    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)

    # تسجيل الـ Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transfer_bp)
    app.register_blueprint(accounts_bp)

    return app
