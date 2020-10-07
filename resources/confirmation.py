import traceback
from libs.mailgun import MailgunException
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from models.confirmation import ConfirmationModel
from models.user import UserModel
from resources.user import USER_NOT_FOUND
from schemas import ConfirmationSchema

CONFIRMATION_NOT_FOUND = "Confirmation reference not found."
EXPIRED = "The link has expried."
ALREADY_CONFIRMED = "Registration has already been confirmed."
RESEND_SUCCESS = "We have sent another confirmation email."
RESEND_ERROR = "There was an error resending the confirmation email."

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": CONFIRMATION_NOT_FOUND}, 404

        if confirmation.expired:
            return {"message": EXPIRED}, 404

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 404

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"content-Type": "text/html"}
        return make_response(
            render_template(
                "confirmation_path.html",
                email=confirmation.user.email
            ),
            200,
            headers
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ]
            },
        )

    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message", ALREADY_CONFIRMED}, 499
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": RESEND_SUCCESS}, 201

        except MailgunException as e:
            return {"message", str(e)}, 500
            
        except:
            traceback.print_exc()
            return {"message": RESEND_ERROR}, 500
