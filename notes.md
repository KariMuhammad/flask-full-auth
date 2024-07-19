# Steps for Forgot password API

1. Send a POST request to `/api/v1/auth/forgotpassword` with the email address.
2. The user receives an email with a reset token.
3. Send a PUT request to `/api/v1/auth/resetpassword/:resettoken` with the new password.
4. The password gets updated in the database.

# Steps for Reset password API

1. Send a PUT request to `/api/v1/auth/resetpassword/:resettoken` with the new password.
2. The password gets updated in the database.

```

```
