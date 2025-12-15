from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # استبدل بمفتاح قوي

# قاعدة بيانات بسيطة في الذاكرة (يمكن استبدالها بقاعدة حقيقية لاحقًا)
users = {}
balances = {}

# الصفحة الرئيسية / تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "اسم المستخدم أو كلمة المرور خاطئة"
    return render_template('login.html')

# تسجيل مستخدم جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "المستخدم موجود مسبقًا"
        users[username] = generate_password_hash(password)
        balances[username] = 1000  # رصيد افتراضي
        return redirect(url_for('login'))
    return render_template('register.html')

# لوحة التحكم
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    balance = balances.get(user, 0)
    return render_template('dashboard.html', user=user, balance=balance)

# عملية التحويل / السحب
@app.route('/transfer', methods=['POST'])
def transfer():
    if 'username' not in session:
        return redirect(url_for('login'))
    sender = session['username']
    recipient = request.form['recipient']
    amount = float(request.form['amount'])

    if recipient not in balances:
        return "المستلم غير موجود"
    if balances[sender] < amount:
        return "رصيدك غير كافٍ"

    balances[sender] -= amount
    balances[recipient] += amount
    return redirect(url_for('dashboard'))

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
