from flask import current_app as app
from extensions import db
from uuid import uuid4
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_by_username(cls, username: str) -> 'User':
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email: str) -> 'User':
        return cls.query.filter_by(email=email).first()
    
    def save(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()
    
    def get_reset_token(self) -> str:
        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        return serializer.dumps(self.email, salt='reset-password')
    
    @staticmethod
    def verify_reset_token(cls, token) -> str:
        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        
        try:
            email = serializer.loads(token, salt='reset-password', max_age=600)
        except:
            return None
        
        return cls.query.filter_by(email=email).first()
        
    
class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    jti = db.Column(db.String(351), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<TokenBlocklist {self.jti}>'
    
    @classmethod
    def is_jti_blacklisted(cls, jti: str) -> bool:
        return bool(cls.query.filter_by(jti=jti).first())
    
    def save(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()
    
    
class PasswordResetTokens(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    token = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<PasswordResetTokens {self.token}>'
    
    @classmethod
    def get_by_user_email(cls, user_email: str) -> User:
        return cls.query.filter_by(user_email=user_email).first()
    
    def save(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()