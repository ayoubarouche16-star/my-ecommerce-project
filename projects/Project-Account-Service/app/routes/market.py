# app/routes/market.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps

market_bp = Blueprint("market", __name__, url_prefix="/market")

# =========================
# بيانات افتراضية لأسعار العملات والمؤشرات
# =========================
market_data = {
    "EURUSD": {"price": 1.12, "change": 0.001, "volume": 1000, "high": 1.123, "low": 1.118, "timestamp": datetime.utcnow().isoformat()},
    "GBPUSD": {"price": 1.30, "change": -0.002, "volume": 800, "high": 1.305, "low": 1.295, "timestamp": datetime.utcnow().isoformat()},
    "GOLD": {"price": 1950.0, "change": 5.0, "volume": 50, "high": 1960.0, "low": 1940.0, "timestamp": datetime.utcnow().isoformat()},
    "SILVER": {"price": 25.0, "change": -0.1, "volume": 200, "high": 25.5, "low": 24.8, "timestamp": datetime.utcnow().isoformat()},
}

# =========================
# بيانات تاريخية افتراضية (للرسوم البيانية)
# =========================
market_history = {
    symbol: [] for symbol in market_data
}

# =========================
# تنبيهات الأسعار (لكل مستخدم)
# =========================
price_alerts = {}

# =========================
# Decorator للتحكم في الوصول حسب نوع المستخدم
# =========================
def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(current_user, "role", "user")
            if user_role not in allowed_roles:
                return jsonify({"error": "غير مصرح لك بالوصول إلى هذه الصفحة"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =========================
# Route: عرض البيانات الأساسية للسوق
# =========================
@market_bp.route("/", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def get_market_overview():
    return jsonify({
        "market": market_data,
        "last_update": datetime.utcnow().isoformat()
    }), 200

# =========================
# Route: تحديث البيانات الافتراضية للسوق
# =========================
@market_bp.route("/update", methods=["POST"])
@login_required
@roles_required("admin", "vip")
def update_market():
    data = request.get_json() or {}
    for symbol, info in market_data.items():
        delta = data.get(symbol, {}).get("change", info["change"])
        info["price"] += delta
        info["high"] = max(info["high"], info["price"])
        info["low"] = min(info["low"], info["price"])
        info["timestamp"] = datetime.utcnow().isoformat()

        # حفظ السجل التاريخي
        market_history[symbol].append({
            "price": info["price"],
            "timestamp": info["timestamp"]
        })

    return jsonify({
        "message": "تم تحديث بيانات السوق",
        "market": market_data
    }), 200

# =========================
# Route: ملخص السوق
# =========================
@market_bp.route("/market-summary", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def market_summary():
    summary = {}
    for symbol, info in market_data.items():
        summary[symbol] = {
            "current_price": info["price"],
            "daily_change": info["change"],
            "volume": info["volume"],
            "high": info["high"],
            "low": info["low"],
            "last_update": info["timestamp"]
        }
    return jsonify({
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat()
    }), 200

# =========================
# Route: تفاصيل رمز واحد
# =========================
@market_bp.route("/symbol/<symbol>", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def get_symbol(symbol):
    symbol = symbol.upper()
    if symbol not in market_data:
        return jsonify({"error": "الرمز غير موجود"}), 404
    return jsonify({
        "symbol": symbol,
        "data": market_data[symbol]
    }), 200

# =========================
# Route: السجل التاريخي للرمز
# =========================
@market_bp.route("/history/<symbol>", methods=["GET"])
@login_required
@roles_required("user", "admin", "vip")
def get_symbol_history(symbol):
    symbol = symbol.upper()
    return jsonify({
        "symbol": symbol,
        "history": market_history.get(symbol, [])
    }), 200

# =========================
# Route: إضافة تنبيه سعري
# =========================
@market_bp.route("/alerts", methods=["POST"])
@login_required
@roles_required("user", "vip")
def add_price_alert():
    data = request.get_json() or {}
    symbol = data.get("symbol", "").upper()
    target_price = data.get("price")

    if not symbol or target_price is None:
        return jsonify({"error": "بيانات غير مكتملة"}), 400

    user_id = current_user.get_id()
    price_alerts.setdefault(user_id, []).append({
        "symbol": symbol,
        "target_price": target_price,
        "created_at": datetime.utcnow().isoformat()
    })

    return jsonify({"message": "تم إضافة التنبيه بنجاح"}), 201

# =========================
# Route: عرض تنبيهات المستخدم
# =========================
@market_bp.route("/alerts", methods=["GET"])
@login_required
def list_price_alerts():
    user_id = current_user.get_id()
    return jsonify({
        "alerts": price_alerts.get(user_id, [])
    }), 200
