# app/routes/dashboard.py

from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime

# ربط مباشر مع Trades
from app.routes.trades import get_user_trades as get_real_user_trades, trades_logs
from app.routes.accounts import notify  # لإرسال إشعارات فورية

# WebSocket
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import socketio  # يجب أن يكون لديك socketio معرف في app/__init__.py

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# بيانات افتراضية لإحصاءات المستخدم
user_stats = {}
user_trades_history = {}  # لتخزين جميع الصفقات المفتوحة والمغلقة لكل مستخدم

def get_user_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {
            "total_trades": 0,
            "open_trades": 0,
            "closed_trades": 0,
            "balance": 10000.0,
            "profit_loss_total": 0.0,
            "buy_trades": 0,
            "sell_trades": 0,
            "last_update": datetime.utcnow().isoformat()
        }
    return user_stats[user_id]

def get_user_trades(user_id):
    """تخزين ومتابعة جميع الصفقات لكل مستخدم"""
    trades = get_real_user_trades(user_id)
    if user_id not in user_trades_history:
        user_trades_history[user_id] = trades
    else:
        user_trades_history[user_id] = trades
    return user_trades_history[user_id]

def log_trade_dashboard(user_id):
    """تحديث إحصاءات Dashboard بناءً على الصفقات الحقيقية"""
    stats = get_user_stats(user_id)
    trades = get_user_trades(user_id)
    
    stats["total_trades"] = len(trades)
    stats["open_trades"] = len([t for t in trades if t["status"]=="open"])
    stats["closed_trades"] = len([t for t in trades if t["status"]=="closed"])
    stats["profit_loss_total"] = sum([t.get("profit_loss",0) for t in trades if t["status"]=="closed"])
    stats["buy_trades"] = len([t for t in trades if t["type"]=="buy"])
    stats["sell_trades"] = len([t for t in trades if t["type"]=="sell"])
    stats["balance"] = sum([t.get("amount_usd",0) + t.get("profit_loss",0) for t in trades if t["status"]=="closed"]) + \
                       sum([t.get("amount_usd",0) for t in trades if t["status"]=="open"])
    stats["last_update"] = datetime.utcnow().isoformat()

    for trade in trades:
        if not trade.get("notified", False):
            status_text = "مفتوحة" if trade["status"]=="open" else "مغلقة"
            notify(user_id, f"⚡ تم تحديث صفقة {trade['symbol']} ({trade['type']})، الحالة: {status_text}, الربح/الخسارة: {trade.get('profit_loss',0)} USD")
            trade["notified"] = True

            socketio.emit(
                "trade_update",
                {"trade": trade, "dashboard": stats},
                room=f"user_{user_id}"
            )

    return stats

@dashboard_bp.route("/", methods=["GET"])
@login_required
def dashboard_overview():
    stats = log_trade_dashboard(current_user.id)
    trades = get_user_trades(current_user.id)
    return render_template("dashboard.html", dashboard=stats, trades=trades)

@dashboard_bp.route("/update_trades", methods=["POST"])
@login_required
def update_trades():
    stats = log_trade_dashboard(current_user.id)
    trades = get_user_trades(current_user.id)
    return jsonify({"message": "تم تحديث الإحصاءات تلقائيًا مع الإشعارات الفورية", "dashboard": stats, "trades": trades}), 200

@dashboard_bp.route("/summary", methods=["GET"])
@login_required
def trades_summary():
    stats = log_trade_dashboard(current_user.id)
    trades = get_user_trades(current_user.id)
    summary = {
        "total_trades": stats["total_trades"],
        "open_trades": stats["open_trades"],
        "closed_trades": stats["closed_trades"],
        "buy_trades": stats["buy_trades"],
        "sell_trades": stats["sell_trades"],
        "profit_loss_total": stats["profit_loss_total"],
        "balance": stats["balance"],
        "last_update": stats["last_update"]
    }
    return jsonify({"summary": summary, "trades": trades}), 200

@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        stats = log_trade_dashboard(current_user.id)
        trades = get_user_trades(current_user.id)
        emit("dashboard_init", {"dashboard": stats, "trades": trades}, room=f"user_{current_user.id}")

@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")

def send_live_dashboard_update(user_id):
    stats = log_trade_dashboard(user_id)
    trades = get_user_trades(user_id)
    socketio.emit(
        "live_dashboard_update",
        {"dashboard": stats, "trades": trades},
        room=f"user_{user_id}"
    )

# --- HTML + JS محسّن مع مؤشرات إضافية ومخططات تفاعلية ---
"""
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم التداول - احترافية</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; color: #111; margin:0; padding:0; }
        .dashboard { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        h1 { text-align: center; color: #4b0082; }
        .stats { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-bottom: 30px; }
        .card { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 3px 15px rgba(0,0,0,0.1); flex: 1 1 200px; text-align:center; transition: transform 0.2s; }
        .card:hover { transform: scale(1.05); }
        .card span { font-weight: bold; font-size: 1.3em; display:block; margin-top:5px; }
        .trades { margin-top: 40px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #ddd; }
        th { background: #7c3aed; color: #fff; }
        .profit { color: green; font-weight:bold; }
        .loss { color: red; font-weight:bold; }
        .charts { display: flex; gap: 20px; flex-wrap: wrap; margin-top:30px; justify-content:center; }
        .chart-card { background:#fff; padding:20px; border-radius:12px; box-shadow:0 3px 15px rgba(0,0,0,0.1); flex:1 1 400px; }
        .market-trends { margin-top: 40px; display:flex; gap:20px; flex-wrap:wrap; justify-content:center; }
        .trend-card { background:#fff; padding:15px; border-radius:12px; box-shadow:0 3px 15px rgba(0,0,0,0.1); flex:1 1 250px; text-align:center; }
        .trend-card span { font-weight:bold; font-size:1.1em; display:block; margin-top:5px; }
    </style>
</head>
<body>
<div class="dashboard">
    <h1>لوحة تحكم التداول الاحترافية</h1>
    <div class="stats">
        <div class="card">إجمالي الصفقات: <span id="total_trades">{{ dashboard.total_trades }}</span></div>
        <div class="card">الصفقات المفتوحة: <span id="open_trades">{{ dashboard.open_trades }}</span></div>
        <div class="card">الصفقات المغلقة: <span id="closed_trades">{{ dashboard.closed_trades }}</span></div>
        <div class="card">الرصيد: <span id="balance">{{ dashboard.balance }}</span> USD</div>
        <div class="card">إجمالي الربح/الخسارة: <span id="profit_loss_total">{{ dashboard.profit_loss_total }}</span> USD</div>
    </div>

    <div class="charts">
        <div class="chart-card">
            <h3>تطور الربح/الخسارة</h3>
            <canvas id="profitChart"></canvas>
        </div>
        <div class="chart-card">
            <h3>تغير الرصيد</h3>
            <canvas id="balanceChart"></canvas>
        </div>
        <div class="chart-card">
            <h3>الأسعار التاريخية</h3>
            <canvas id="historicalChart"></canvas>
        </div>
        <div class="chart-card">
            <h3>مخطط آخر 24 ساعة لكل أصل</h3>
            <canvas id="last24hChart"></canvas>
        </div>
    </div>

    <div class="market-trends">
        <div class="trend-card">اتجاه السوق: <span id="market_direction">...</span></div>
        <div class="trend-card">آخر الصفقات: <span id="recent_trades">...</span></div>
    </div>

    <div class="trades">
        <h2>الصفقات</h2>
        <table>
            <thead>
                <tr>
                    <th>الرمز</th>
                    <th>النوع</th>
                    <th>الحالة</th>
                    <th>المبلغ</th>
                    <th>الربح/الخسارة</th>
                </tr>
            </thead>
            <tbody id="trades_table">
                {% for trade in trades %}
                <tr id="trade_{{ trade.id }}">
                    <td>{{ trade.symbol }}</td>
                    <td>{{ trade.type }}</td>
                    <td>{{ trade.status }}</td>
                    <td>{{ trade.amount_usd }}</td>
                    <td class="{{ 'profit' if trade.profit_loss > 0 else 'loss' }}">{{ trade.profit_loss }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<script>
    const socket = io();

    socket.on("connect", () => {
        console.log("متصل بالـ WebSocket!");
    });

    socket.on("trade_update", (data) => {
        console.log("تحديث جديد:", data);
        updateDashboard(data.dashboard);
        updateTrades(data.trades);
        updateCharts(data.trades);
        updateMarketTrends(data.trades);
        updateLast24hChart(data.trades);
    });

    socket.on("dashboard_init", (data) => {
        console.log("تحميل بيانات اللوحة:", data);
        updateDashboard(data.dashboard);
        updateTrades(data.trades);
        updateCharts(data.trades);
        updateMarketTrends(data.trades);
        updateLast24hChart(data.trades);
    });

    function updateDashboard(stats) {
        document.getElementById("total_trades").innerText = stats.total_trades;
        document.getElementById("open_trades").innerText = stats.open_trades;
        document.getElementById("closed_trades").innerText = stats.closed_trades;
        document.getElementById("balance").innerText = stats.balance.toFixed(2);
        document.getElementById("profit_loss_total").innerText = stats.profit_loss_total.toFixed(2);
    }

    function updateTrades(trades) {
        const tbody = document.getElementById("trades_table");
        tbody.innerHTML = "";
        trades.forEach(trade => {
            const row = document.createElement("tr");
            row.id = `trade_${trade.id}`;
            row.innerHTML = `
                <td>${trade.symbol}</td>
                <td>${trade.type}</td>
                <td>${trade.status}</td>
                <td>${trade.amount_usd}</td>
                <td class="${trade.profit_loss > 0 ? 'profit' : 'loss'}">${trade.profit_loss}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // Charts.js
    let profitChart = new Chart(document.getElementById('profitChart').getContext('2d'), {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'الربح/الخسارة', data: [], borderColor: 'green', backgroundColor: 'rgba(0,255,0,0.1)', tension:0.3 }] },
        options: { responsive: true, plugins: { legend: { display: true } } }
    });

    let balanceChart = new Chart(document.getElementById('balanceChart').getContext('2d'), {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'الرصيد', data: [], borderColor: '#7c3aed', backgroundColor: 'rgba(124,58,237,0.1)', tension:0.3 }] },
        options: { responsive: true, plugins: { legend: { display: true } } }
    });

    let historicalChart = new Chart(document.getElementById('historicalChart').getContext('2d'), {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'سعر تاريخي', data: [], borderColor: '#ff9900', backgroundColor: 'rgba(255,153,0,0.1)', tension:0.3 }] },
        options: { responsive: true, plugins: { legend: { display: true } } }
    });

    // مخطط آخر 24 ساعة لكل أصل
    let last24hChart = new Chart(document.getElementById('last24hChart').getContext('2d'), {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { beginAtZero: false }
            }
        }
    });

    function updateCharts(trades) {
        const labels = trades.map((t,i)=>`صفقة ${i+1}`);
        const profitData = trades.map(t=>t.profit_loss);
        const balanceData = trades.map(t=>t.amount_usd + t.profit_loss);
        const historicalData = trades.map(t=>t.amount_usd); // كمثال للسعر التاريخي

        profitChart.data.labels = labels;
        profitChart.data.datasets[0].data = profitData;
        profitChart.update();

        balanceChart.data.labels = labels;
        balanceChart.data.datasets[0].data = balanceData;
        balanceChart.update();

        historicalChart.data.labels = labels;
        historicalChart.data.datasets[0].data = historicalData;
        historicalChart.update();
    }

    function updateMarketTrends(trades) {
        const marketDirectionEl = document.getElementById("market_direction");
        const recentTradesEl = document.getElementById("recent_trades");

        const recent = trades.slice(-5);
        const direction = recent.reduce((acc, t) => acc + t.profit_loss, 0) >= 0 ? "صاعد" : "هابط";
        marketDirectionEl.innerText = direction;
        recentTradesEl.innerText = recent.map(t=>t.symbol).join(", ");
    }

    function updateLast24hChart(trades) {
        const symbols = [...new Set(trades.map(t => t.symbol))];
        const labels = Array.from({length:24}, (_,i)=>`${i}h`);

        last24hChart.data.labels = labels;
        last24hChart.data.datasets = symbols.map(sym => {
            const symTrades = trades.filter(t => t.symbol === sym);
            const data = Array.from({length:24}, (_,i)=> {
                const trade = symTrades[i];
                return trade ? trade.amount_usd : null;
            });
            const lastPrice = data[data.length-1] || 0;
            const color = data[data.length-1] >= (data[data.length-2] || 0) ? 'green' : 'red';
            return {
                label: sym,
                data: data,
                borderColor: color,
                backgroundColor: color === 'green' ? 'rgba(0,255,0,0.1)' : 'rgba(255,0,0,0.1)',
                tension:0.3
            };
        });
        last24hChart.update();
    }
</script>
</body>
</html>
"""
