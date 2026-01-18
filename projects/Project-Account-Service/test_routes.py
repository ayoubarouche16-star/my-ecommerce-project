# test_routes.py

import requests

BASE_URL = "http://127.0.0.1:5000"

# ============================
# اختبار Auth Routes
# ============================
def test_auth_routes():
    print("🔹 اختبار Auth Routes")

    payload = {"username": "testuser", "password": "123456"}

    # تسجيل مستخدم جديد
    r = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print("Register:", r.status_code, r.json())

    # تسجيل الدخول
    r = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print("Login:", r.status_code, r.json())

    token = None
    user_id = None
    if r.status_code == 200:
        user_id = r.json().get("user_id")
        token = r.json().get("token")  # JWT token

    return user_id, token


# ============================
# اختبار Dashboard Routes
# ============================
def test_dashboard_routes(user_id, token):
    print("🔹 اختبار Dashboard Routes")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    r = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    print("Dashboard Home:", r.status_code, r.json())


# ============================
# اختبار Transfer Routes
# ============================
def test_transfer_routes(user_id, token):
    print("🔹 اختبار Transfer Routes")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # إرسال تحويل
    payload = {"user_id": str(user_id), "amount": 100}
    r = requests.post(f"{BASE_URL}/transfer/", json=payload, headers=headers)
    try:
        print("Send Transfer:", r.status_code, r.json())
    except Exception:
        print("Send Transfer: لا يوجد JSON صالح، الرد:", r.text)

    # سجل التحويلات
    r = requests.get(f"{BASE_URL}/transfer/history", params={"user_id": user_id}, headers=headers)
    try:
        print("Transfer History:", r.status_code, r.json())
    except Exception:
        print("Transfer History: لا يوجد JSON صالح، الرد:", r.text)

    # أرصدة المحافظ
    r = requests.get(f"{BASE_URL}/transfer/wallets", params={"user_id": user_id}, headers=headers)
    try:
        print("Wallet Balances:", r.status_code, r.json())
    except Exception:
        print("Wallet Balances: لا يوجد JSON صالح، الرد:", r.text)


# ============================
# تشغيل كل الاختبارات
# ============================
if __name__ == "__main__":
    user_id, token = test_auth_routes()
    if user_id and token:
        test_dashboard_routes(user_id, token)
        test_transfer_routes(user_id, token)
    print("========== الانتهاء من الاختبارات ==========")
