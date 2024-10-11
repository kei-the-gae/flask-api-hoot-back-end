from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
import os
import jwt
import psycopg2, psycopg2.extras
import bcrypt
from auth_middleware import token_required

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database='POSTGRES_DATABASE',
        user=os.getenv('POSTGRES_USERNAME'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return connection

@app.route('/auth/signup', methods=['POST'])
def signup():
    try:
        new_user_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s;', (new_user_data['username'],))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            return jsonify({'error': 'Username already taken'}), 400
        hashed_password = bcrypt.hashpw(bytes(new_user_data['password'], 'utf-8'), bcrypt.gensalt())
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id, username', (new_user_data['username'], hashed_password.decode('utf-8')))
        created_user = cursor.fetchone()
        connection.commit()
        token = jwt.encode(created_user, os.getenv('JWT_SECRET'))
        return jsonify({'token': token, 'user': created_user}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 401
    finally:
        connection.close()

@app.route('/auth/signin', methods=['POST'])
def signin():
    try:
        sign_in_form_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s;', (sign_in_form_data['username'],))
        existing_user = cursor.fetchone()
        if existing_user is None:
            return jsonify({'error': 'Invalid credentials.'}), 401
        password_is_valid = bcrypt.checkpw(bytes(sign_in_form_data['password'], 'utf-8'), bytes(existing_user['password'], 'utf-8'))
        if not password_is_valid:
            return jsonify({'error': 'Invalid credentials.'}), 401
        token = jwt.encode({'username': existing_user['username'], 'id': existing_user['id']}, os.getenv('JWT_SECRET'))
        return jsonify({'token': token}), 201
    except Exception as err:
        return jsonify({'error': 'Invalid credentials.'}), 401
    finally:
        connection.close()

@app.route('/')
def index():
    return 'Hello, world!'

app.run()
