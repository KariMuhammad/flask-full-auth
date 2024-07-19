from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_current_user
account = Blueprint('account', __name__, url_prefix="/")

@account.get("/profile")
@jwt_required()
def authenticated_profile():
    user = get_current_user()
        
    return jsonify({
        'username': user.get('username'),
        "user": user
    })

@account.get("/profile/<int:id>")
def get_profile_by_id(id: int):
    pass

@account.put("/profile/<int:id>")
def update_profile_by_id(id: int):
    pass

@account.delete("/profile")
def delete_profile():
    pass