import flask
from flask_restful import Api
from resources.user import Cart, Item, Users, User, Login, Items
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager

# Flask setting
app = flask.Flask(__name__)

# Flask restful setting
api = Api(app)


app.config["DEBUG"] = True # Able to reload flask without exit the process
app.config["JWT_SECRET_KEY"] = "secret_key" #JWT token setting 

# Swagger setting
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Mall Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

# User Login
api.add_resource(Login, "/login")
docs.register(Login)

# 查詢物品
api.add_resource(Items, "/items")
docs.register(Items)

# 購物車
api.add_resource(Cart, "/cart")
docs.register(Cart)

# URL(router)
api.add_resource(Users, "/users")
docs.register(Users)
api.add_resource(User, "/user/<int:id>")
docs.register(User)

if __name__ == '__main__':
    # JWT token setting
    jwt = JWTManager().init_app(app)
    app.run(host='127.0.0.1', port=5000)
