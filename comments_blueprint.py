from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required

comments_blueprint = Blueprint('comments_blueprint', __name__)

@comments_blueprint.route('/hoots/<hoot_id>/comments', methods=['POST'])
@token_required
def create_comment(hoot_id):
    try:
        new_comment_data = request.get_json()
        new_comment_data['author'] = g.user['id']
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''
                       INSERT INTO comments (hoot, author, text)
                        VALUES (%s, %s, %s)
                        RETURNING *
                       ''',
                       (hoot_id, new_comment_data['author'], new_comment_data['text'])
        )
        created_comment = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({'comment': created_comment}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500
