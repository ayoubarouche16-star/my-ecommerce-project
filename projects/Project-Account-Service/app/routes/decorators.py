from functools import wraps
from flask import request, jsonify
import jwt

SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # ضع مفتاح سري قوي هنا

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # الحصول على التوكن من الهيدر Authorization
        if "Authorization" in request.headers:
            token_header = request.headers.get("Authorization")
            if token_header.startswith("Bearer "):
                token = token_header.split(" ")[1]
        if not token:
            return jsonify({"error": "التوكن مفقود"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = str(data.get("user_id"))
        except Exception as e:
            return jsonify({"error": "توكن غير صالح أو منتهي"}), 401
        return f(*args, **kwargs)
    return decorated_function
