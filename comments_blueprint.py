from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required

comments_blueprint = Blueprint('comments_blueprint', __name__)


