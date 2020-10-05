from flask_restful import Resource
from models.store import StoreModel
from schemas.store import StoreSchema

# strings as constants
CANNOT_BE_EMPTY = "{} cannot be empty."
NOT_FOUND = "Store not found."
ALREADY_EXISTS = "{} already exists."
ERROR_WITH_DB = "An error ocurred while {} store."
STORE_DELETED = "Store deleted successfully."

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store)
        return {"message": NOT_FOUND}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": ALREADY_EXISTS.format(name)}, 400

        store = StoreModel(name=name)  # There is no init method
        try:
            store.save_to_db()
        except:
            return {"message": ERROR_WITH_DB.format("inserting")}, 500

        return store_schema.dump(store), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        try:
            if store:
                store.delete_from_db()
            else:
                return {"message": NOT_FOUND}, 404
        except:
            return {"message": ERROR_WITH_DB.format("deleting")}, 500

        return {"message": STORE_DELETED}


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": store_list_schema.dump(StoreModel.find_all())}
