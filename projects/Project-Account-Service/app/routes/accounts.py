# app/routes/accounts.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

# db سيتم استخدامه من main بعد تهيئة التطبيق (Factory Pattern)
# لذا هنا لا نستورد db مباشرة لتجنب circular import

accounts_bp = Blueprint("accounts", __name__, url_prefix="/accounts")

# قاعدة بيانات مؤقتة للمستخدمين
user_accounts = {}
account_logs = {}
notifications = {}

def get_user_account(user_id):
    if user_id not in user_accounts:
        user_accounts[user_id] = {
            "real": 0.0,
            "demo": 10000.0,
            "account_type": "standard",  # standard | vip
            "status": "active",          # active | suspended
            "currency": "USD",
            "kyc_verified": False,
            "daily_withdraw_limit": 5000,
            "created_at": datetime.utcnow().isoformat()
        }
    return user_accounts[user_id]

def log_action(user_id, action, details=""):
    if user_id not in account_logs:
        account_logs[user_id] = []
    account_logs[user_id].append({
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })

def notify(user_id, message):
    if user_id not in notifications:
        notifications[user_id] = []
    notifications[user_id].append({
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    })

@accounts_bp.route("/balance", methods=["GET"])
@login_required
def account_balance():
    """عرض الرصيد الحالي للمستخدم"""
    account = get_user_account(current_user.id)
    return jsonify(account), 200

@accounts_bp.route("/deposit", methods=["POST"])
@login_required
def deposit():
    """إيداع مبلغ في الحساب"""
    data = request.get_json()
    account_type = data.get("type")
    amount = float(data.get("amount", 0))

    if account_type not in ["real", "demo"]:
        return jsonify({"error": "نوع الحساب غير صالح"}), 400
    if amount <= 0:
        return jsonify({"error": "المبلغ يجب أن يكون أكبر من صفر"}), 400

    account = get_user_account(current_user.id)
    account[account_type] += amount

    log_action(current_user.id, "deposit", f"{amount} to {account_type}")
    notify(current_user.id, f"تم إيداع {amount}$ في حسابك {account_type}")

    return jsonify({"message": "تم الإيداع بنجاح", "balance": account}), 200

@accounts_bp.route("/withdraw", methods=["POST"])
@login_required
def withdraw():
    """سحب مبلغ من الحساب"""
    data = request.get_json()
    account_type = data.get("type")
    amount = float(data.get("amount", 0))

    account = get_user_account(current_user.id)

    if not account["kyc_verified"]:
        return jsonify({"error": "يجب توثيق الحساب (KYC) قبل السحب"}), 403

    if amount > account["daily_withdraw_limit"]:
        return jsonify({"error": "تجاوزت الحد اليومي للسحب"}), 403

    if account_type not in ["real", "demo"]:
        return jsonify({"error": "نوع الحساب غير صالح"}), 400
    if amount <= 0 or account[account_type] < amount:
        return jsonify({"error": "الرصيد غير كافٍ"}), 400

    account[account_type] -= amount

    log_action(current_user.id, "withdraw", f"{amount} from {account_type}")
    notify(current_user.id, f"تم سحب {amount}$ من حسابك")

    return jsonify({"message": "تم السحب بنجاح", "balance": account}), 200

@accounts_bp.route("/upgrade", methods=["POST"])
@login_required
def upgrade_account():
    """ترقية الحساب إلى VIP"""
    account = get_user_account(current_user.id)
    account["account_type"] = "vip"
    account["daily_withdraw_limit"] = 20000

    log_action(current_user.id, "upgrade", "VIP account")
    notify(current_user.id, "تمت ترقية حسابك إلى VIP")

    return jsonify({"message": "تمت الترقية إلى VIP"}), 200

@accounts_bp.route("/verify-kyc", methods=["POST"])
@login_required
def verify_kyc():
    """توثيق الحساب"""
    account = get_user_account(current_user.id)
    account["kyc_verified"] = True

    log_action(current_user.id, "kyc", "verified")
    notify(current_user.id, "تم توثيق حسابك بنجاح")

    return jsonify({"message": "KYC Verified"}), 200

@accounts_bp.route("/logs", methods=["GET"])
@login_required
def logs():
    """سجل النشاط"""
    return jsonify(account_logs.get(current_user.id, [])), 200

@accounts_bp.route("/notifications", methods=["GET"])
@login_required
def get_notifications():
    """إشعارات المستخدم"""
    return jsonify(notifications.get(current_user.id, [])), 200
