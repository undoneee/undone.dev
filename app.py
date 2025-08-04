#!/usr/bin/env python3
"""
A simple web application for user management with intentional bugs
"""
import hashlib
import sqlite3
from flask import Flask, request, jsonify, session
import os
import bcrypt

app = Flask(__name__)
# Fixed: Use environment variable for secret key with fallback for development
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

DATABASE = 'users.db'

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using bcrypt - Fixed: Strong hashing algorithm"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Fixed: SQL injection vulnerability - using parameterized queries
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    
    try:
        query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
        cursor.execute(query, (username, hashed_password, email))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Fixed: Get user by username only, then verify password separately
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):  # user[2] is the password field
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({'message': 'Login successful', 'user': user[1]}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users - Fixed: Added authentication check"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({'users': users}), 200

def calculate_fibonacci(n):
    """Calculate fibonacci number - Fixed: Efficient iterative implementation with memoization"""
    if n <= 1:
        return n
    
    # Use iterative approach for better performance
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@app.route('/fibonacci/<int:n>')
def fibonacci(n):
    """Get fibonacci number"""
    if n < 0:
        return jsonify({'error': 'Number must be non-negative'}), 400
    
    # Fixed: Add upper limit check to prevent DoS
    if n > 1000:
        return jsonify({'error': 'Number too large (max 1000)'}), 400
    
    result = calculate_fibonacci(n)
    return jsonify({'fibonacci': result}), 200

def process_user_data(users):
    """Process user data - Fixed: Logic error in filtering"""
    active_users = []
    for user in users:
        # Fixed: Using comparison (==) instead of assignment (=)
        if user.get('status') == 'active':
            active_users.append(user)
    return active_users

if __name__ == '__main__':
    init_db()
    # Fixed: Use environment variable to control debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1')  # Also fixed: bind to localhost by default