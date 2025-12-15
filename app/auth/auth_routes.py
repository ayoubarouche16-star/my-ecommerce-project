from flask import Flask, request, jsonify
from app.auth.auth_controller import register_user, login_user

auth_app = Flask(__name__)

# -------------------------
# تسجيل مستخدم
# -------------------------
@auth_app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    result = register_user(name, email, password)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

# -------------------------
# تسجيل الدخول
# -------------------------
@auth_app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    result = login_user(email, password)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)
from flask import Blueprint
from .auth_controller import register_user, login_user

auth_app = Blueprint('auth_app', __name__)

# مثال على مسارات تسجيل الدخول والتسجيل
@auth_app.route('/register', methods=['POST'])
def register():
    return register_user()

@auth_app.route('/login', methods=['POST'])
def login():
    return login_user()
from flask import Blueprint
from app.auth.auth_controller import register_user, login_user

auth_app = Blueprint('auth_app', __name__)

auth_app.route('/register', methods=['POST'])(register_user)
auth_app.route('/login', methods=['POST'])(login_user)
# app/auth/auth_routes.py
from flask import Blueprint
from app.auth.auth_controller import register_user, login_user

auth_app = Blueprint("auth_app", __name__)

# التسجيل
auth_app.add_url_rule("/register", "register", register_user, methods=["POST"])
# تسجيل الدخول
auth_app.add_url_rule("/login", "login", login_user, methods=["POST"])
from flask import Blueprint, request, jsonify
from .auth_controller import register_user, login_user

auth_app = Blueprint('auth', __name__)

@auth_app.route('/register', methods=['POST'])
def register():
    data = request.json
    return jsonify(register_user(data['username'], data['password']))

@auth_app.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify(login_user(data['username'], data['password']))
