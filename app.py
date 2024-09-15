from flask import Flask, request, render_template

from flask_pydantic import validate
from pydantic import ValidationError

from config import Config

from common.jsontools import *

# 引入实体类
from entityModels import *

app = Flask(__name__)
app.config.from_object(Config)

import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB
from datetime import datetime

import hashlib

pool = PooledDB(
    creator=pymysql,
    # 创建最大连接
    maxconnections=6,
    mincached=2,
    maxcached=3,
    maxshared=4,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=0,
    # 这一坨会传给上面的 pymysql
    host='localhost',
    port=13306,
    user='root',
    passwd='admin',
    database='binance_demo',
    charset='utf8',
    # 让查询结果是一个 dict
    cursorclass=cursors.DictCursor
)


@app.route('/')
def home():
    # Passing dynamic content to the Jinja template
    return render_template('index.html',
                           title="My Flask App",
                           heading="Welcome to My Flask App",
                           content="This is a sample Jinja page.",
                           items=['Flask', 'Jinja2', 'Python'],
                           user="John Doe")


@app.route('/users/login', methods=['POST'])
def login():
    # Parse the JSON request data
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(response(code=400, message="Username and password are required")), 400

    sql = "SELECT username, password_hash FROM users WHERE username = %s"
    
    conn = pool.connection()

    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if user:
            # Hash the provided password with the dummy hash function
            hashed_password = dummy_hash_password(password)
            
            # Compare the hashed passwords
            if hashed_password == user['password_hash']:
                return jsonify(response(code=200, message="Login successful")), 200
            else:
                return jsonify(response(code=401, message="Invalid credentials")), 401
        else:
            return jsonify(response(code=404, message="User not found")), 404

    except pymysql.Error as e:
        conn.rollback()
        return jsonify(response(code=500, message=f"Database error: {e}")), 500

    finally:
        conn.close()


@app.route('/users/register', methods=['POST'])
def register():
    # Parse the JSON request data
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(response(code=400, message="Username and password are required")), 400

    # Hash the password
    password_hash = dummy_hash_password(password)

    sql_check_user = "SELECT username FROM users WHERE username = %s"
    sql_insert_user = "INSERT INTO users (username, password_hash, created_time, is_active) VALUES (%s, %s, %s, %s)"

    conn = pool.connection()

    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Check if the user already exists
        cursor.execute(sql_check_user, (username,))
        user = cursor.fetchone()

        if user:
            return jsonify(response(code=409, message="Username already exists")), 409

        # Insert new user into the database
        cursor.execute(sql_insert_user, (username, password_hash, datetime.now(), True))
        conn.commit()

        return jsonify(response(code=201, message="User registered successfully")), 201

    except pymysql.Error as e:
        conn.rollback()
        return jsonify(response(code=500, message=f"Database error: {e}")), 500

    finally:
        conn.close()


def response(code, message, data=None):
    return {
        'code': code,
        'message': message,
        'data': data
    }

# Dummy hash function using SHA-256
def dummy_hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1')  # 默认值为 '127.0.0.1'，如果未找到 'HOST' 配置项
    port = app.config.get('PORT', 5000)  # 默认值为 5000，如果未找到 'PORT' 配置项
    app.run(host=host, port=port)
