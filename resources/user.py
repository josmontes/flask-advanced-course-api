import traceback
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

from models.user import UserModel
from schemas.user import UserSchema
from blacklist import BLACKLIST
from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel

# strings as constants
USER_NOT_FOUND = "User not found."
ALREADY_EXISTS = "{} already exists."
ERROR_WITH_DB = "An error ocurred while {} user."
USER_SUCCESS = "User {} successfully."
REGISTER_SUCCESS = "Account created, please confirm by checking your email."
INVALID_CREDENTIALS = "Invalid credentials."
USER_LOGGED_OUT = "User {} successfully logged out."
NOT_CONFIRMED = "You have to confirm your email."

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {"message": ALREADY_EXISTS.format(user.username)}, 400
        if UserModel.find_by_email(user.email):
            return {"message": ALREADY_EXISTS.format(user.email)}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": REGISTER_SUCCESS}, 201
        except MailgunException as e:
            user.delete_from_db()  # rollback
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": ERROR_WITH_DB.format("inserting")}, 500


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


class UserLogin(Resource):
    @classmethod
    def post(cls):
        login_user = user_schema.load(request.get_json(), partial=("email",))

        user = UserModel.find_by_username(login_user.username)
        if user and safe_str_cmp(user.password, login_user.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(
                    identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            else:
                return {"message": NOT_CONFIRMED}, 400
        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        # jti is "JWT ID" unique identifier for a JWT
        jti = get_raw_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": USER_SUCCESS.format("logged out")}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {"access_token": new_token}, 200
