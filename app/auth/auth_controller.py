import sqlite3
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import jwt
from app.database.db import get_connection

JWT_SECRET = "change_this_to_a_strong_secret"
JWT_EXP_DAYS = 7  # صلاحية التوكن 7 أيام

# -------------------------
# تسجيل مستخدم جديد
# -------------------------
def register_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = bcrypt.hash(password)
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password_hash, datetime.utcnow()))
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "name": name, "email": email}
    except sqlite3.IntegrityError:
        return {"error": "Email already registered"}
    finally:
        conn.close()

# -------------------------
# تسجيل الدخول
# -------------------------
def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return {"error": "Invalid credentials"}

    if not bcrypt.verify(password, user["password_hash"]):
        return {"error": "Invalid credentials"}

    payload = {
        "id": user["id"],
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(days=JWT_EXP_DAYS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}
from flask import request, jsonify
from app.models.user import User
import jwt
import datetime

SECRET_KEY = "YOUR_SECRET_KEY"  # غيّرها لمفتاح قوي

def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.find_by_username(username):
        return jsonify({"error": "User already exists"}), 400

    User.create(username, password)
    return jsonify({"message": "User created successfully"}), 201

def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.find_by_username(username)
    if not user or not User.verify_password(password, user['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})
# app/auth/auth_controller.py
from flask import request, jsonify
from app.models.user import User
import jwt
import datetime

# غيّر هذه القيمة لمفتاح قوي في الإنتاج
JWT_SECRET = "CHANGE_THIS_TO_A_STRONG_SECRET"
JWT_ALGORITHM = "HS256"
JWT_EXP_SECONDS = 60 * 60 * 24  # 1 day

def register_user():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.find_by_username(username):
        return jsonify({"error": "user already exists"}), 400

    uid = User.create(username, password)
    return jsonify({"message": "user created", "id": uid}), 201

def login_user():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    row = User.find_by_username(username)
    if not row:
        return jsonify({"error": "invalid credentials"}), 401

    if not User.verify_password(password, row["password_hash"]):
        return jsonify({"error": "invalid credentials"}), 401

    payload = {
        "sub": row["id"],
        "username": row["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jsonify({"token": token, "user": {"id": row["id"], "username": row["username"]}})
from app.models.user import create_user, get_user_by_username, hash_password
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "change_this_to_a_strong_secret"

def register_user(username, password):
    if get_user_by_username(username):
        return {"error": "user already exists"}
    create_user(username, password)
    return {"message": "user created"}

def login_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return {"error": "invalid credentials"}
    if hash_password(password) != user[2]:
        return {"error": "invalid credentials"}
    # إنشاء JWT
    payload = {
        "user_id": user[0],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"token": token, "user": {"id": user[0], "username": user[1]}}
