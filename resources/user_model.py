from marshmallow import Schema, fields

# ItemSchema
class LoginSchema(Schema):
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)

class ItemGetSchema(Schema):
    name = fields.Str(example="string")


class ItemPostSchema(Schema):
    prod_name = fields.Str(doc="prod_name", example="string", required=True)
    price = fields.Str(doc="price", example="integer", required=True)
    qty = fields.Str(doc="qty", example="integer", required=True)
    category = fields.Str(doc="category", example="string")
    note = fields.Str(doc="note", example="string")


class ItemPatchSchema(Schema):
    name = fields.Str(doc="prod_name", example="string")
    price = fields.Str(doc="price", example="integer")
    qty = fields.Str(doc="qty", example="integer")
    category = fields.Str(doc="category", example="string")
    note = fields.Str(doc="note", example="string")

class ItemBuySchema(Schema):
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)
    prod_name = fields.Str(doc="prod_name", example="string", required=True)
    price = fields.Str(doc="price", example="integer", required=True)
    qty = fields.Str(doc="qty", example="integer", required=True)


# UserSchema
class LoginSchema(Schema):
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)

class UserGetSchema(Schema):
    name = fields.Str(example="string")


class UserPostSchema(Schema):
    name = fields.Str(doc="name", example="string", required=True)
    gender = fields.Str(doc="gender", example="string", required=True)
    account = fields.Str(doc="account", example="string", required=True)
    password = fields.Str(doc="password", example="string", required=True)
    birth = fields.Str(doc="birth", example="string")
    note = fields.Str(doc="note", example="string")


class UserPatchSchema(Schema):
    name = fields.Str(doc="name", example="string")
    gender = fields.Str(doc="gender", example="string")
    account = fields.Str(doc="account", example="string")
    password = fields.Str(doc="password", example="string")
    birth = fields.Str(doc="birth", example="string")
    note = fields.Str(doc="note", example="string")


# Response
class UserGetResponse(Schema):
    message = fields.Str(example="success")
    datatime = fields.Str(example="1970-01-01T00:00:00.000000")
    data = fields.List(fields.Dict())


class UserCommonResponse(Schema):
    message = fields.Str(example="success")


