import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError
from flask_uploads import configure_uploads, patch_request_class
from dotenv import load_dotenv

from ma import ma
from db import db
from resources.user import UserRegister, UserLogin, UserLogout, User, TokenRefresh
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.image import Avatar, ImageUpload, Image, AvatarUpload
from blacklist import BLACKLIST
from libs.images import IMAGE_SET

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(app, size=10 * 1024 * 1024)
configure_uploads(app, IMAGE_SET)
api = Api(app)
jwt = JWTManager(app)
db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def marshmallow_validation_handler(err):
    return jsonify(err.messages), 400


@jwt.token_in_blacklist_loader
def token_in_blacklist_callback(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST
    # if true it will go to the revoked loader


# Users
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Confirmation, "/confirm/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")

# Items
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")

# Stores
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")

# Images
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")

if __name__ == "__main__":
    app.run(port=5000)
