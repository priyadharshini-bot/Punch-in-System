from flask import Flask, render_template, redirect, url_for, request, session, send_file
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT NOT NULL,
        punch_type TEXT CHECK(punch_type IN ('in', 'out')),
        timestamp TEXT NOT NULL,
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    )''')
    # Add admin user if not exists
    cur.execute("SELECT * FROM employees WHERE emp_id = 'admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO employees (emp_id, name, password, role) VALUES (?, ?, ?, ?)",
                    ('admin', 'Admin User', generate_password_hash('admin123'), 'admin'))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        password = request.form['password']
        conn = sqlite3.connect('attendance.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session['emp_id'] = user[1]
            session['name'] = user[2]
            session['role'] = user[4]
            return redirect(url_for('dashboard' if user[4] == 'admin' else 'employee'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/employee', methods=['GET', 'POST'])
def employee():
    if 'emp_id' not in session or session['role'] != 'employee':
        return redirect(url_for('login'))
    emp_id = session['emp_id']
    name = session['name']
    if request.method == 'POST':
        punch_type = request.form['punch_type']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect('attendance.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO attendance (emp_id, punch_type, timestamp) VALUES (?, ?, ?)",
                    (emp_id, punch_type, timestamp))
        conn.commit()
        conn.close()
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()
    cur.execute("SELECT punch_type, timestamp FROM attendance WHERE emp_id = ? ORDER BY timestamp DESC LIMIT 10", (emp_id,))
    records = cur.fetchall()
    conn.close()
    return render_template('employee.html', name=name, records=records)

@app.route('/dashboard')
def dashboard():
    if 'emp_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()
    cur.execute("SELECT emp_id, punch_type, timestamp FROM attendance ORDER BY timestamp DESC")
    records = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', records=records)

@app.route('/export')
def export():
    if 'emp_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('attendance.db')
    cur = conn.cursor()
    cur.execute("SELECT emp_id, punch_type, timestamp FROM attendance")
    records = cur.fetchall()
    conn.close()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Employee ID', 'Punch Type', 'Timestamp'])
    cw.writerows(records)
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='attendance.csv', as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# app.py
from flask import Flask
from add_employee import register_routes

app = Flask(__name__)

@app.route('/')
def home():
    return "Punch In System is Live!"

# Register routes from add_employee.py
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
