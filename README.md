1. `git clone https://github.com/KariMuhammad/flask-full-auth.git`
2. `cd flask-full-auth`
3. `pip install -r requirements.txt`

Run the Server

1. `export FLASK_APP=main.py`
2. `flask run`

Migrate the Database

1. `open new terminal`
2. `export FLASK_APP=main.py`
3. `flask shell`
4. `from models import User, TokenBlocklist, PasswordResetTokens`
5. `db.create_all()`
6. `exit()` || `ctrl + z`

## API Endpoints

### Register User

```http
POST /auth/register

{
    "name": "John Doe",
    "email": "
    "password": "password"
    "password_confirm": "password"
    "phone": "08012345678"
}
```

Response

```json
{
  "message": "Successfully User created"
}
```

### Login User

```http
POST /auth/login

{
    "email": "demo@gmail.com",
    "password": "password"
}
```

Response

```json
{
 "access_token": "eyJ********************"
 "refresh_token": "eyJ********************"
}
```

### Profile

```http
GET /profile
Authorization Bearer Token
```

Response

```json
{
    "user": {
        "id": 1,
       "name": "John Doe",
       "email": "john@gmail.com",
       "phone": "08012345678",
       "created_at": "2021-09-07T14:00:00",
    }

    "username": "John Doe",
}
```

### Logout

```http
POST /auth/logout
Authorization Bearer Token
```

Response

```json
{
  "message": "Successfully logged out"
}
```

### Refresh Token

```http
POST /auth/refresh
Authorization Bearer Refresh_Token
```

Response

```json
{
  "access_token": "eyJ********************"
}
```

### Forgot Password

```http
POST /auth/forgot-password

{
    "email": "john@gmail.com"
}
```

Response

```json
{
  "message": "Email sent with password reset instructions",
  "reset_token": "ImtpbW9vbWFyMDA3QGdtYWlsLmNvbSI.bSmtpb************"
}
```

### Reset Password

```http
POST /auth/reset-password/reset_token

{
    "new_password": "newpassword",
    "new_password_confirmation": "newpassword"
}
```

Response

```json
{
  "message": "Password updated successfully"
}
```
