from flask import Flask, request, jsonify, render_template_string
import sqlite3
import hashlib
import os
import re
import bcrypt

app = Flask(__name__)

# Bug 1: Hardcoded secret key - security vulnerability
app.secret_key = "my_secret_key_123"

# Fixed: SQL injection vulnerability - now using parameterized queries
def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    try:
        cursor = conn.cursor()
        # FIXED: Using parameterized query to prevent SQL injection
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        return user
    finally:
        # FIXED: Connection properly closed in finally block
        conn.close()

# Fixed: Insecure password hashing - now using bcrypt with salt
def hash_password(password):
    # FIXED: Using bcrypt with salt for secure password hashing
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    # FIXED: Secure password verification using bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Bug 4: No input validation - can cause crashes
def process_email(email):
    # VULNERABLE: No validation, can cause issues with malformed emails
    return email.lower().strip()

# Fixed: Resource leak - now using proper connection management
def get_all_users():
    conn = sqlite3.connect('users.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return users
    finally:
        # FIXED: Connection properly closed in finally block
        conn.close()

@app.route('/')
def index():
    return render_template_string('''
        <h1>User Management System</h1>
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
        <form action="/register" method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <input type="email" name="email" placeholder="Email">
            <button type="submit">Register</button>
        </form>
    ''')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # FIXED: Using secure password verification
    if username and password:
        # Simple check - in real app would query database
        if username == "admin" and verify_password(password, hash_password("admin123")):
            return f"Welcome {username}! You are logged in."
    
    return "Login failed"

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    if username and password and email:
        # Bug 7: No password strength validation
        hashed_password = hash_password(password)
        processed_email = process_email(email)
        
        # Bug 8: No duplicate username check
        # In real app, would insert into database
        return f"User {username} registered with email {processed_email}"
    
    return "Registration failed"

@app.route('/user/<user_id>')
def get_user(user_id):
    # Bug 9: SQL injection vulnerability
    user = get_user_by_id(user_id)
    if user:
        return jsonify({"user": user})
    return jsonify({"error": "User not found"})

@app.route('/users')
def list_users():
    # Bug 10: Resource leak - connection not closed
    users = get_all_users()
    return jsonify({"users": users})

# Bug 11: Debug mode enabled in production - security risk
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)