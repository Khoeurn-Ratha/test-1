from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# កំណត់ Database (បើនៅលើ Render វារត់តាម Cloud DB, បើលើ PC វារត់ SQLite ធម្មតា)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://database_test_qkul_user:QYOpjtF6mJP5ql8562UwFPCRtgKuXo5l@dpg-da8gf8oae00c73csaur0-a/database_test_qkul')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# បង្កើត Model សម្រាប់เก็บទិន្នន័យ Trade
class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    pair = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)

# បង្កើត Database Tables ពេលបើកកូដដំបូង
with app.app_context():
    db.create_all()

# --- HTML Templates (ដាក់បញ្ចូលក្នុង File តែមួយ) ---
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Journal - Input</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col items-center justify-center p-4">
    <div class="w-full max-w-md bg-slate-800 p-8 rounded-2xl shadow-xl border border-slate-700">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold tracking-wide text-indigo-400">📊 Trading Journal</h1>
            <a href="/admin" class="text-sm bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg transition">View Data</a>
        </div>
        <form action="/" method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Date</label>
                <input type="date" name="date" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Pair / Asset</label>
                <input type="text" name="pair" placeholder="e.g. XAUUSD, EURUSD" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Price</label>
                <input type="number" step="any" name="price" placeholder="e.g. 2350.50" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-slate-300 mb-1">Notes / Strategy</label>
                <textarea name="notes" rows="3" placeholder="Smart Money Concepts, Breakout..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"></textarea>
            </div>
            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-lg transition shadow-lg shadow-indigo-600/30">
                Save Trade
            </button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Trades</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-6">
    <div class="max-w-6xl mx-auto">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-indigo-400">📈 Admin Dashboard (User Trades)</h1>
            <a href="/" class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-4 py-2 rounded-lg transition">
                + Add New Trade
            </a>
        </div>
        <div class="bg-slate-800 rounded-2xl shadow-xl border border-slate-700 overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-700/50 text-slate-400 text-sm uppercase tracking-wider border-b border-slate-700">
                            <th class="py-3 px-6">ID</th>
                            <th class="py-3 px-6">Date</th>
                            <th class="py-3 px-6">Pair</th>
                            <th class="py-3 px-6">Price</th>
                            <th class="py-3 px-6">Notes</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-700 text-slate-300">
                        {% for trade in trades %}
                        <tr class="hover:bg-slate-700/30 transition">
                            <td class="py-4 px-6 font-mono text-indigo-400">#{{ trade.id }}</td>
                            <td class="py-4 px-6">{{ trade.date }}</td>
                            <td class="py-4 px-6 font-semibold text-white">{{ trade.pair }}</td>
                            <td class="py-4 px-6 font-mono text-emerald-400">{{ trade.price }}</td>
                            <td class="py-4 px-6 text-slate-400">{{ trade.notes }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="5" class="text-center py-8 text-slate-500">No trades recorded yet.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        pair = request.form['pair']
        price = float(request.form['price'])
        notes = request.form.get('notes', '')

        new_trade = Trade(date=date, pair=pair, price=price, notes=notes)
        db.session.add(new_trade)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template_string(INDEX_HTML)

@app.route('/admin')
def admin():
    all_trades = Trade.query.all()
    return render_template_string(ADMIN_HTML, trades=all_trades)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)