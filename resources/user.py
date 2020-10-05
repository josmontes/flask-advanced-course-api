from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)
from marshmallow import ValidationError
from models.user import UserModel
from schemas.user import UserSchema
from blacklist import BLACKLIST

# strings as constants
NOT_FOUND = "User not found."
ALREADY_EXISTS = "{} already exists."
ERROR_WITH_DB = "An error ocurred while {} user."
USER_SUCCESS = "User {} successfully."
INVALID_CREDENTIALS = "Invalid credentials."
USER_LOGGED_OUT = "User {} successfully logged out."

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            data = user_schema.load(request.get_json())
        except ValidationError as error:
            return error.messages, 404
        if UserModel.find_by_username(data["username"]):
            return {"message": ALREADY_EXISTS.format(data["username"])}, 400

        user = UserModel(**data)
        try:
            user.save_to_db()
            return {"message": USER_SUCCESS.format("created")}, 201
        except:
            return {"message": ERROR_WITH_DB.format("inserting")}, 500


class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            data = user_schema.load(request.get_json())
        except ValidationError as error:
            return error.messages, 404
        user = UserModel.find_by_username(data["username"])
        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        # jti is "JWT ID" unique identifier for a JWT
        jti = get_raw_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": USER_SUCCESS.format("logged out")}, 200


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND}, 404
        return user_schema.dump(user)

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_SUCCESS.format("deleted")}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {"access_token": new_token}, 200
