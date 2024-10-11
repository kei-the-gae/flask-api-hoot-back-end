from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

hoots_blueprint = Blueprint('hoots_blueprint', __name__)

@hoots_blueprint.route('/hoots', methods=['GET'])
def hoots_index():
    return jsonify({'message': 'hoots index lives here'})

@hoots_blueprint.route('/hoots', methods=['POST'])
@token_required
def create_hoot():
    try:
        new_hoot = request.json
        new_hoot['author'] = g.user['id']
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''
                       INSERT INTO hoots (author, title, text, category)
                       VALUES (%s, %s, %s, %s)
                       RETURNING *
                       ''',
                       (new_hoot['author'], new_hoot['title'], new_hoot['text'], new_hoot['category'])
        )
        created_hoot = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({'hoot': created_hoot}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500
