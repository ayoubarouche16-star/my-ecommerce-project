from flask import Blueprint, request, jsonify
from app.routes.decorators import login_required

transfer_bp = Blueprint("transfer_bp", __name__)

# قاعدة بيانات مؤقتة للاختبارات
users = {
    "1": {
        "balance": 1000.0,
        "transactions": [
            {"id": 1, "amount": 100, "type": "credit"},
            {"id": 2, "amount": 50, "type": "debit"}
        ]
    }
}

# ============================
# Route: إرسال التحويل
# ============================
@transfer_bp.route("/", methods=["POST"])
@login_required
def send_transfer():
    data = request.json
    user_id = str(data.get("user_id"))
    amount = data.get("amount", 0)

    # التحقق أن user_id في التوكن يطابق user_id المرسل
    if user_id != request.user_id:
        return jsonify({"error": "غير مخول"}), 403

    if user_id not in users:
        return jsonify({"error": "المستخدم غير موجود"}), 400

    if not amount or amount <= 0:
        return jsonify({"message": "جميع الحقول مطلوبة"}), 400

    users[user_id]["balance"] -= amount
    users[user_id]["transactions"].append({
        "id": len(users[user_id]["transactions"]) + 1,
        "amount": amount,
        "type": "debit"
    })
    return jsonify({"message": "تم التحويل بنجاح", "balance": users[user_id]["balance"]}), 200

# ============================
# Route: سجل التحويلات
# ============================
@transfer_bp.route("/history", methods=["GET"])
@login_required
def transfer_history():
    user_id = request.args.get("user_id")

    if user_id != request.user_id:
        return jsonify({"error": "غير مخول"}), 403

    if user_id not in users:
        return jsonify({"error": "المستخدم غير موجود"}), 400

    return jsonify({"transactions": users[user_id]["transactions"]}), 200

# ============================
# Route: أرصدة المحافظ
# ============================
@transfer_bp.route("/wallets", methods=["GET"])
@login_required
def wallet_balances():
    user_id = request.args.get("user_id")

    if user_id != request.user_id:
        return jsonify({"error": "غير مخول"}), 403

    if user_id not in users:
        return jsonify({"error": "المستخدم غير موجود"}), 400

    return jsonify({"balance": users[user_id]["balance"]}), 200
