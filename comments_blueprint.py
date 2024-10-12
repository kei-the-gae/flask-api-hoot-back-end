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

@comments_blueprint.route('/hoots/<hoot_id>/comments/<comment_id>', methods=['PUT'])
@token_required
def update_comment(hoot_id, comment_id):
  try:
    updated_comment_data = request.json
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM comments WHERE id = %s', (comment_id,))
    comment_to_update = cursor.fetchone()
    if comment_to_update is None:
      return jsonify({'error': 'Comment not found.'}), 404
    if comment_to_update['author'] is not g.user['id']:
      return jsonify({'error': 'Unauthorized.'}), 401
    cursor.execute('UPDATE comments SET text = %s WHERE id = %s RETURNING *',
                   (updated_comment_data['text'], comment_id))
    updated_comment = cursor.fetchone()
    connection.commit()
    connection.close()
    return jsonify({'comment': updated_comment}), 201
  except Exception as err:
    return jsonify({'error': str(err)}), 500
