from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from app.main import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # deposit, withdraw, transfer
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="pending")  # pending, approved

def create_tables():
    db.create_all()

def create_user(email, password, balance=0.0):
    user = User(email=email, password=generate_password_hash(password), balance=balance)
    db.session.add(user)
    db.session.commit()
    return user
