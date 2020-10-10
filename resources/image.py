from inspect import trace
import traceback
import os

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs import images
from libs.strings import gettext
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        """
        This endpoint is used to upload an image file. It uses the
        JWT to retrieve user information and save the image in the user's folder.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.png to filename_1.png).
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            # save(self, storage, folder=None, name=None)
            image_path = images.save_image(data["image"], folder=folder)
            # here we only return the basename of the image and hide the internal folder structure from our user
            basename = images.get_basename(image_path)
            return {"message": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:  # forbidden file type
            extension = images.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        """
        Returns requested image if it exists inside logged in user's folder
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not images.is_filename_safe(filename):
            return {"message": gettext("image_illegal_filename").format(filename)}, 400

        try:
            return send_file(images.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": gettext("image_not_found")}, 404

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not images.is_filename_safe(filename):
            return {"message": gettext("image_illegal_filename").format(filename)}, 400

        try:
            print(images.get_path(filename, folder=folder))
            os.remove(images.get_path(filename, folder=folder))
            return {"message": gettext("image_deleted")}
        except FileNotFoundError:
            return {"message": gettext("image_not_found")}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("image_delete_error")}, 500


class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        """
        Used to upload user avatars
        """
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        avatar_path = images.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": gettext("avatar_delete_error")}, 500

        try:
            ext = images.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = images.save_image(
                data["image"], folder=folder, name=avatar)
            basename = images.get_basename(avatar_path)
            return {"message": gettext("avatar_uploaded").format(basename)}
        except UploadNotAllowed:
            extension = images.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Avatar(Resource):
    @classmethod
    def get(cls, user_id: int):
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = images.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {"message": gettext("avatar_not_found")}, 404
