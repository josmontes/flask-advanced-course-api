from ma import ma
from marshmallow import pre_dump
from models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "activated")
        load_instance = True

    @pre_dump
    def pre_dump(self, user: UserModel):
        user.confirmation = [user.most_recent_confirmation]
        return user
