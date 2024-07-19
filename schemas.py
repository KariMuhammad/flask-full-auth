from marshmallow import Schema, fields

class UserSchema(Schema):
    username = fields.String()
    email = fields.Email()
    phone = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
