from flask import Flask, jsonify
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

from extensions import db, jwt
from auth import auth
from account import account
from users import users

from schemas import UserSchema
from models import User, TokenBlocklist
import os

def create_app():    
    app = Flask(__name__)        
    
    app.config.from_prefixed_env()
    
    # Init database
    db.init_app(app)
    # Init JWT
    jwt.init_app(app)
    
    
    
    # Init Routes
    app.register_blueprint(auth)
    
    # Profiles
    app.register_blueprint(account)
    
    # Users
    app.register_blueprint(users)
    
    # JWT Check Blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()
        
        return token is not None
    
    # Automatic Load User
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        user = User.query.filter_by(username=identity).first()
        return UserSchema().dump(user)
    
    # add more claims to the JWT
    # Executed when ~creating the JWT
    @jwt.additional_claims_loader
    def make_additional_claims(identity):
        if identity == "admin":
            return {'role': 'admin'}
        else:            
            return {'role': 'user'}
    
    # jwt error handling
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has expired.',
            'error': 'token_expired'
        }), 401
        
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Signature verification failed.',
            'error': 'token_invalid'
        }), 401
        
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'message': 'Request does not contain an access token.',
            'error': 'authorization_required'
        }), 401

    return app


# main.py or app.py
if __name__ == "__main__":
    from run import app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))