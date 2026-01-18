# app/config.py

class Config:
    DEBUG = True
    SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # ضع مفتاح سري قوي هنا
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
