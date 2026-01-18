# app/routes/trades.py

from flask import Blueprint, request, jsonify
from datetime import datetime

# 🔹 استخدام نفس نظام الحماية المعتمد في المشروع
from app.routes.decorators import login_required

trades_bp = Blueprint("trades_bp", __name__, url_prefix="/trades")

# بيانات افتراضية للصفقات
user_trades = {}
trades_logs = {}

# ربط بالرصيد والحسابات المؤقتة (سيتم ربطها لاحقًا مع SQLAlchemy)
from app.routes.accounts import get_user_account, log_action, notify

# أسعار افتراضية للعملات مقابل USD (في الإنتاج تربط بـ API خارجي)
currency_rates = {
    "USD": 1.0,
    "EUR": 1.1,
    "BTC": 30000.0,
    "ETH": 2000.0
}

def get_user_trades(user_id):
    if user_id not in user_trades:
        user_trades[user_id] = []
    return user_trades[user_id]

def log_trade(user_id, action, trade_id, details=""):
    if user_id not in trades_logs:
        trades_logs[user_id] = []
    trades_logs[user_id].append({
        "trade_id": trade_id,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })

@trades_bp.route("/", methods=["GET"])
@login_required
def list_trades():
    """عرض جميع الصفقات للمستخدم"""
    user_id = request.user_id
    trades = get_user_trades(user_id)
    return jsonify({"trades": trades, "last_update": datetime.utcnow().isoformat()}), 200

@trades_bp.route("/new", methods=["POST"])
@login_required
def new_trade():
    """فتح صفقة جديدة"""
    data = request.get_json()
    symbol = data.get("symbol")
    amount = float(data.get("amount", 0))
    trade_type = data.get("type")  # buy or sell
    leverage = float(data.get("leverage", 1))
    stop_loss = data.get("stop_loss")  # optional
    take_profit = data.get("take_profit")  # optional
    currency = data.get("currency", "USD").upper()  # العملة المطلوبة

    user_id = request.user_id

    if currency not in currency_rates:
        return jsonify({"error": "عملة غير مدعومة"}), 400

    if not symbol or amount <= 0 or trade_type not in ["buy", "sell"]:
        return jsonify({"error": "بيانات الصفقة غير صحيحة"}), 400

    # التحقق من رصيد المستخدم
    account = get_user_account(user_id)
    if not account["kyc_verified"]:
        return jsonify({"error": "يجب توثيق الحساب (KYC) قبل فتح الصفقات"}), 403

    # تحويل المبلغ للعملة الافتراضية USD للحساب
    amount_usd = amount * currency_rates[currency]
    if amount_usd > account["real"]:
        return jsonify({"error": "الرصيد غير كافٍ"}), 400

    # Hedging
    existing_trades = [
        t for t in get_user_trades(user_id)
        if t["symbol"] == symbol and t["status"] == "open"
    ]
    if existing_trades and trade_type != existing_trades[-1]["type"] and account["account_type"] != "vip":
        return jsonify({"error": "الحساب Standard لا يسمح بفتح صفقتين متعاكستين على نفس الرمز"}), 403

    account["real"] -= amount_usd

    trade_id = len(get_user_trades(user_id)) + 1

    trade = {
        "trade_id": trade_id,
        "symbol": symbol,
        "amount": amount,
        "currency": currency,
        "amount_usd": amount_usd,
        "type": trade_type,
        "leverage": leverage,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "opened_at": datetime.utcnow().isoformat(),
        "status": "open",
        "profit_loss": 0.0,
        "account_type": account["account_type"]
    }

    trades = get_user_trades(user_id)
    trades.append(trade)

    if account["real"] < 100:
        notify(user_id, "⚠️ تنبيه: رصيدك منخفض جدًا بعد فتح الصفقة!")

    log_trade(user_id, "open", trade_id, f"{trade_type} {symbol} {amount} {currency} (Leverage: {leverage})")
    notify(user_id, f"تم فتح صفقة {trade_type} على {symbol} بمبلغ {amount} {currency} (Leverage: {leverage})")

    return jsonify({"message": "تم فتح الصفقة بنجاح", "trade": trade}), 201

@trades_bp.route("/close/<int:trade_id>", methods=["POST"])
@login_required
def close_trade(trade_id):
    """إغلاق صفقة مفتوحة"""
    user_id = request.user_id
    trades = get_user_trades(user_id)

    trade = next((t for t in trades if t["trade_id"] == trade_id), None)
    if not trade:
        return jsonify({"error": "صفقة غير موجودة"}), 404
    if trade["status"] == "closed":
        return jsonify({"error": "الصفقة مغلقة بالفعل"}), 400

    trade["profit_loss"] = trade["amount_usd"] * 0.05 * (1 if trade["type"] == "buy" else -1)
    trade["status"] = "closed"
    trade["closed_at"] = datetime.utcnow().isoformat()

    account = get_user_account(user_id)
    account["real"] += trade["amount_usd"] + trade["profit_loss"]

    log_trade(user_id, "close", trade_id, f"Profit/Loss: {trade['profit_loss']}$ ({trade['currency']})")
    notify(user_id, f"تم إغلاق صفقة {trade['symbol']}، الربح/الخسارة: {trade['profit_loss']}$")

    return jsonify({"message": "تم إغلاق الصفقة بنجاح", "trade": trade}), 200
