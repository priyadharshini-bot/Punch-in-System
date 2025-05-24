import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('attendance.db')
cur = conn.cursor()

# CHANGE THESE VALUES AS NEEDED
emp_id = 'priya dharshini'
name = 'Priya'
password = '123456'
role = 'employee'

hashed = generate_password_hash(password)
cur.execute("INSERT INTO employees (emp_id, name, password, role) VALUES (?, ?, ?, ?)",
            (emp_id, name, hashed, role))

conn.commit()
conn.close()

print("Employee added successfully!")
# add_employee.py
from flask import request, jsonify

def register_routes(app):
    @app.route('/add-employee', methods=['POST'])
    def add_employee():
        data = request.json
        # Add employee logic here
        return jsonify({'status': 'success', 'employee': data})
