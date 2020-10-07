from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, fresh_jwt_required
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema

# strings as constants
CANNOT_BE_EMPTY = "{} cannot be empty."
ITEM_NOT_FOUND = "Item not found."
ALREADY_EXISTS = "{} already exists."
ERROR_WITH_DB = "An error ocurred while {} item."
ITEM_DELETED = "Item deleted successfully."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item)
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": ALREADY_EXISTS.format(name)}, 400

        item_json = request.get_json()
        item_json["name"] = name
        item = item_schema.load(item_json)
       
        try:
            item.save_to_db()
        except:
            return {"message": ERROR_WITH_DB.format("inserting")}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        try:
            item = ItemModel.find_by_name(name)
            if item:
                item.delete_from_db()
            else:
                return {"message": ITEM_NOT_FOUND}, 404
        except:
            return {"message": ERROR_WITH_DB.format("deleting")}, 500

        return {"message": ITEM_DELETED}

    @classmethod
    def put(cls, name: str):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        try:
            if item:
                item.price = item_json["price"]
            else:
                item_json["name"] = name
                item = item_schema.load(item_json)

            item.save_to_db()
        except:
            return {"message": ERROR_WITH_DB.format("updating")}, 500

        return item.item_schema.dump(item)


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_list_schema(ItemModel.find_all())}, 200
