from flask import Blueprint, jsonify, request, current_app as app, url_for, redirect
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from itsdangerous import URLSafeTimedSerializer
from models import User, TokenBlocklist, PasswordResetTokens
from schemas import RegisterUserSchema, SignGoogleSchema
from flask_mail import Mail, Message
from extensions import oauth
from authlib.jose import JoseError

import os

auth = Blueprint('auth', __name__, url_prefix="/auth")

@auth.post("/register")
def register():
    data = request.get_json()
    schema = RegisterUserSchema()
    
    try:
        schema.load(data)
    except Exception as e:
        return jsonify({"message": "Validation error", "error": e.messages}), 400
    
    new_user = User(
        username=data.get("username"),
        email=data.get("email"),
        phone=data.get("phone")
    )
        
    new_user.set_password(data.get("password"))
    
    # Send Confirmation Email
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    confirm_url = f"{app.config['FRONTEND_URL']}/auth/confirm-email/{serializer.dumps(new_user.email, salt='email-confirm')}"
    msg = Message('Confirm Email', sender="noreply@demo.com", recipients=[new_user.email])
    url_for = f"<a href='{confirm_url}'>Click here to confirm your email</a>"
    
    msg.body = f"Click here to confirm your email: {url_for}"
    mail = Mail(app)
    mail.send(msg)
    
    try:
        mail.send(msg)
        new_user.save()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify({"message": "User created, but failed to send confirmation email", "error": str(e)}), 500

@auth.post("/login")
def login():
    
    data = request.get_json()
    user = User.get_by_email(data.get("email"))
    
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    if not user.check_password(data.get("password")):
        return jsonify({"message": "Invalid credentials"}), 401
    
    print("=======USER=======", user.username)
    # JWT
    access_token = create_access_token(identity=user.username)
    refresh_token = create_refresh_token(identity=user.username)

    return jsonify(
        {
            "message": "Logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200


@auth.get("/logout")
@jwt_required()
def logout():
    jwt = get_jwt();
    jti = jwt.get('jti')
    
    token = TokenBlocklist(jti=jti)
    token.save()
    return jsonify({"message": "Successfully logged out"}), 200


@auth.get("/refresh")
@jwt_required(refresh=True) # send refresh token instead of access token
def refresh():

    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify({"access_token": access_token}), 200
    
@auth.get("/confirm-email/<token>")
def confirm_email(token):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)
    except:
        return jsonify({"message": "Invalid or expired token"}), 401
    
    user = User.get_by_email(email)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    user.email_confirmed = True
    user.save()
    
    return jsonify({"message": "Email confirmed"}), 200

@auth.post("/forgot-password")
def forgot_password():
    data = request.get_json()
    user = User.get_by_email(data.get("email"))
    
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    token = user.get_reset_token()
    reset_url = f"{app.config['FRONTEND_URL']}/auth/reset-password/{token}"
    msg = Message('Reset Password', sender="noreply@demo.com", recipients=[user.email])
    url_for = f"<a href='{reset_url}'>Click here to reset your password</a>"
    
    msg.body = f"Click here to reset your password: {url_for}"
    mail = Mail(app)
    
    try:
        mail.send(msg)
        return jsonify({"message": "Reset password email sent", "reset_token": token}), 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify({"message": "Failed to send reset password email", "error": e}), 500
    
    
@auth.get("/reset-password/<token>")
def reset_password(token):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    
    try:
        email = serializer.loads(token, salt="reset-password", max_age=600)
    except:
        return jsonify({"message": "Invalid or expired token"}), 401
    
    user = User.get_by_email(email)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    
    PasswordResetTokens(user_email=email, token=token).save()
    return jsonify({"message": "Password reset successfully, You can go to your app and update your password."}), 200

@auth.post("/reset-password/<token>")
def update_password(token):
    data = request.get_json()
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    
    try:
        email = serializer.loads(token, salt="reset-password", max_age=600)
    except:
        return jsonify({"message": "Invalid or expired token"}), 401
    
    user = User.get_by_email(email)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    password_reset_token = PasswordResetTokens.get_by_user_email(email)
    if password_reset_token is None or password_reset_token.token != token:
        return jsonify({"message": "Invalid or expired token"}), 401
    
    if (data.get("new_password") != data.get("new_password_confirmation")):
        return jsonify({"message": "Passwords do not match"}), 400
        
    user.set_password(data.get("new_password"))
    user.save()
    
    password_reset_token.delete()
    return jsonify({"message": "Password reset successfully"}), 200

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

@auth.get('/google')
def login_with_google():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    print(redirect_uri)
    return google.authorize_redirect(redirect_uri)

@auth.get('/google/authorize')
def google_authorize():
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    google_user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
                
    user = User.make(
        username=user_info.get("name"),
        email=user_info.get("email"),
        phone=user_info.get("id")[:11],
        password=user_info.get("id")
    )
    
    user_dict = {
        "username": user_info.get("name"),
        "email": user_info.get("email"),
        "phone": user_info.get("id")[:11],
        "password": user_info.get("id")
    }
    
        
    schema = SignGoogleSchema()
    try:
        schema.load(user_dict)
    except Exception as e:
        return jsonify({"message": "Validation error", "error": e.messages}), 400
    
    # JWT
    user.save()
    access_token = create_access_token(identity=user_info.get('name'))
    refresh_token = create_refresh_token(identity=user_info.get('name'))
        
    return jsonify({
        "message": "You are authenticated, You can go to your app.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_info
    })