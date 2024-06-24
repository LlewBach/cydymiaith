from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo

class Question:
    def __init__(self, username, title, description, answer_count):
        self.username = username
        self.title = title
        self.description = description
        self.answer_count = answer_count

    
    @staticmethod
    def get_categories():
        try:
            categories = list(mongo.db.categories.find())
            return categories
        except Exception as e:
            print(f"Error in get_categories method: {e}")


    def find_by_id(question_id):
        try:
            question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
            return question
        except Exception as e:
            print(f"Error in find_by_id method: {e}")
            return None

    
    @staticmethod
    def get_list():
        try:
            questions = list(mongo.db.questions.find().sort("_id", -1))
            for question in questions:
                Question.set_time_ago(question)
            return questions
        except Exception as e:
            print(f"Error in get_list method: {e}")
            return []
        

    @staticmethod
    def get_list_by_username(username):
        try:
            questions = list(mongo.db.questions.find({"username": username}).sort("_id, -1"))
            for question in questions:
                Question.set_time_ago(question)
            return questions
        except Exception as e:
            print(f"Error in get_list_by_username method: {e}")
    

    @staticmethod
    def set_time_ago(question):
        try:
            creation_time = question['_id'].generation_time.replace(tzinfo=pytz.utc)
            question['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def increase_answer_count(question_id):
        try:
            mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': 1}})
        except Exception as e:
            print(f"Error in increase_answer_count method: {e}")


    @staticmethod
    def decrease_answer_count(question_id):
        try:
            mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': -1}})
        except Exception as e:
            print(f"Error in decrease_answer_count method: {e}")


    @staticmethod
    def insert_question(username, category, title, description):
        try:
            question = {
                "username": username,
                "category": category,
                "title": title,
                "description": description,
                "answer_count": 0
            }
            mongo.db.questions.insert_one(question)
        except Exception as e:
            print(f"Error in insert_question method: {e}")

    
    @staticmethod
    def get_answer_count(question_id):
        try:
            count = Question.find_by_id(question_id)["answer_count"]
            return count
        except Exception as e:
            print(f"Error in get_answer_count method: {e}")
            return 0


    @staticmethod
    def update_question(question_id, username, title, description):
        try:
            current_answer_count = Question.get_answer_count(question_id)
            submit = {
                "username": username,
                "title": title,
                "description": description,
                "answer_count": current_answer_count
            }
            mongo.db.questions.update_one({"_id": ObjectId(question_id)}, {"$set": submit})
        except Exception as e:
            print(f"Error in delete_question method: {e}")


    @staticmethod
    def delete_question(question_id):
        mongo.db.answers.delete_many({"question_id": ObjectId(question_id)})
        mongo.db.questions.delete_one({"_id": ObjectId(question_id)})
