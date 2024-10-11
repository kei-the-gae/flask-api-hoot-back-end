from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

hoots_blueprint = Blueprint('hoots_blueprint', __name__)

@hoots_blueprint.route('/hoots', methods=['GET'])
def hoots_index():
    return jsonify({'message': 'hoots index lives here'})
