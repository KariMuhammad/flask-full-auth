from flask import request
from marshmallow import Schema, fields, ValidationError
from models import User

class UserSchema(Schema):
    username = fields.String()
    email = fields.Email()
    phone = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

def validate_unique_username(value):
    if User.get_by_username(value) is not None:
        raise ValidationError("Username already exists")

def validate_unique_email(value):
    if User.get_by_email(value) is not None:
        raise ValidationError("Email already exists")

def validate_unique_phone(value):
    if User.get_by_phone(value) is not None:
        raise ValidationError("Phone number already exists")

def validate_confirm_password(value):
    if value != request.get_json().get("password"):
        raise ValidationError("Passwords do not match")

class RegisterUserSchema(Schema):
    username = fields.String(validate=validate_unique_username)
    email = fields.String(validate=validate_unique_email)
    phone = fields.String(validate=validate_unique_phone)
    password = fields.String()
    confirm_password = fields.String(validate=validate_confirm_password)

class SignGoogleSchema(Schema):
    username = fields.String(validate=validate_unique_username)
    email = fields.String(validate=validate_unique_email)
    phone = fields.String(validate=validate_unique_phone)
    password = fields.String()
    
class LoginUserSchema(Schema):
    email = fields.Email()
    password = fields.String()
