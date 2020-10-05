import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db

from resources.user import UserRegister, UserLogin, UserLogout, User, TokenRefresh
from blacklist import BLACKLIST

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///data.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

app.secret_key = "Jose"  # app.config["JWT_SECRET_KEY"]
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


db.init_app(app)

jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def token_in_blacklist_callback(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST
    # if true it will go to the revoked loader


api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
