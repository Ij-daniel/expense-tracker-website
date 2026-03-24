from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "supersecretkey"

CORS(app)
bcrypt = Bcrypt(app)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

# =====================
# LANDING PAGE
# =====================
@app.route('/')
def landing():
    return render_template('landing.html')

# =====================
# REGISTER
# =====================
@app.route('/register', methods=['GET', 'POST'])  
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
            (username, email, password)
        )
        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

# =====================
# LOGIN
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')

    return render_template('login.html')

# =====================
# DASHBOARD
# =====================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])

# =====================
# LOGOUT
# =====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# =====================
# ADD EXPENSE
# =====================
@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO expenses(user_id,description,amount,category) VALUES(%s,%s,%s,%s)",
        (session['user_id'], data['description'], data['amount'], data['category'])
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Expense added"})

# =====================
# GET USER EXPENSES
# =====================
@app.route('/get_expenses')
def get_expenses():
    if 'user_id' not in session:
        return jsonify([])

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM expenses WHERE user_id=%s ORDER BY created_at DESC",
        (session['user_id'],)
    )
    rows = cur.fetchall()
    cur.close()

    expenses = []
    for row in rows:
        expenses.append({
            "id": row[0],
            "description": row[2],
            "amount": float(row[3]),
            "category": row[4],
            "created_at": row[5]
        })

    return jsonify(expenses)

# =====================
# DELETE EXPENSE
# =====================
@app.route('/delete_expense/<int:id>', methods=['DELETE'])
def delete_expense(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM expenses WHERE id=%s AND user_id=%s",
                (id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Deleted"})

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False  # turn off debug for Render production
    )