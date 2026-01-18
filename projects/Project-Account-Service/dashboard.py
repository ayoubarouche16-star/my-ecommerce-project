from flask import Blueprint, jsonify
from app.routes.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# مثال بيانات Dashboard
dashboard_data = {
    "balance": 1000.0,
    "recent_transactions": [
        {"id": 1, "amount": 100, "type": "credit"},
        {"id": 2, "amount": 50, "type": "debit"},
    ]
}

@dashboard_bp.route("/", methods=["GET"])
@login_required
def dashboard_home():
    try:
        return jsonify({"dashboard": dashboard_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
