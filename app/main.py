from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"

# قاعدة بيانات بسيطة للتجربة (استبدلها لاحقًا بقاعدة حقيقية)
users = {}

transactions = []

# الصفحة الرئيسية
@app.route("/")
def index():
    return render_template("index.html")

# تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users.get(username)
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "اسم المستخدم أو كلمة المرور خاطئة"
    return render_template("login.html")

# تسجيل مستخدم جديد
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return "المستخدم موجود مسبقًا"
        users[username] = {"password": generate_password_hash(password)}
        session["user"] = username
        return redirect(url_for("dashboard"))
    return render_template("register.html")

# لوحة التحكم
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    return render_template("dashboard.html", user=user)

# الإعدادات
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        # هنا يمكن إضافة تحديث الإعدادات
        return "تم تحديث الإعدادات"
    return render_template("settings.html")

# الملف الشخصي
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    return render_template("profile.html", user=user)

# التحويلات المالية
@app.route("/transfers", methods=["GET", "POST"])
def transfers():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        amount = request.form["amount"]
        recipient = request.form["recipient"]
        transactions.append({"from": session["user"], "to": recipient, "amount": amount})
        return redirect(url_for("transactions"))
    return render_template("transfers.html")

# العمليات المالية
@app.route("/transactions")
def transactions_view():
    if "user" not in session:
        return redirect(url_for("login"))
    user_transactions = [t for t in transactions if t["from"] == session["user"] or t["to"] == session["user"]]
    return render_template("transactions.html", transactions=user_transactions)

# تسجيل الخروج
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
