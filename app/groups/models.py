from bson.objectid import ObjectId
from app import mongo

class Group:
    def __init__(self):
        pass


    @staticmethod
    def get_all_groups():
        try:
            all_groups = list(mongo.db.groups.find())
            return all_groups
        except Exception as e:
            print(f"Error in get_all_groups method: {e}")


    @staticmethod
    def get_own_groups(username):
        try:
            groups = list(mongo.db.groups.find({"tutor": username}))
            return groups
        except Exception as e:
            print(f"Error in get_own_groups method: {e}")