from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from schemas import UserSchema
from models import User

users = Blueprint('users', __name__, url_prefix="/users")

@users.get("/")
@jwt_required()
def get_users():
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    users = User.query.paginate(
        page= page,
        per_page= per_page,
    )
    
    results = UserSchema().dump(users.items, many=True)
    
    return jsonify({
        "users": results
    }), 200