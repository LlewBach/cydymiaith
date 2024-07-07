from bson.objectid import ObjectId
from app import mongo


class Group:
    @staticmethod
    def get_groups_by_role(role, username):
        try:
            if role == 'Admin':
                groups = list(mongo.db.groups.find())
            elif role == 'Tutor':
                groups = list(mongo.db.groups.find({"tutor": username}))
            elif role == 'Student':
                groups = list(mongo.db.groups.find({"students": username}))
            else:
                groups = []

            return groups
        
        except Exception as e:
            print(f'Error in get_groups_by_role method: {e}')


    @staticmethod
    def get_group_by_id(group_id):
        try:
            group = mongo.db.groups.find_one({"_id": group_id})

            return group
        
        except Exception as e:
            print(f'Error in get_group_by_id method: {e}')


    @staticmethod
    def add_student_to_group(group_id, username):
        try:
            mongo.db.groups.update_one(
                {'_id': ObjectId(group_id)},
                {'$push': {'students': username}}
            )

        except Exception as e:
            print(f'Error in add_student_to_group method: {e}')


    @staticmethod
    def remove_student(group_id, username):
        try:
            mongo.db.groups.update_one(
                {'_id': ObjectId(group_id)},
                {'$pull': {'students': username}}
            )

        except Exception as e:
            print(f'Error in remove_student method: {e}')


    @staticmethod
    def insert_group(tutor, provider, level, year, weekday):
        try:
            group = {
                "tutor": tutor,
                "provider": provider,
                "level": level,
                "year": year,
                "weekday": weekday,
                "students": []
            }
            mongo.db.groups.insert_one(group)
            
        except Exception as e:
            print(f"Error in insert_group method: {e}")

    
    @staticmethod
    def get_levels():
        return list(mongo.db.levels.find())
    

    @staticmethod
    def get_providers():
        return list(mongo.db.providers.find())