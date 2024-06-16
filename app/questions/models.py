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
    def find_by_id(question_id):
        question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
        return question

    
    @staticmethod
    def get_list():
        questions = list(mongo.db.questions.find().sort("_id", -1))
        for question in questions:
            Question.set_time_ago(question)
        print(questions)
        return questions
    

    @staticmethod
    def set_time_ago(question):
        creation_time = question['_id'].generation_time.replace(tzinfo=pytz.utc)
        question['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)

    
    @staticmethod
    def increase_answer_count(question_id):
        mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': 1}})


    @staticmethod
    def decrease_answer_count(question_id):
        mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': -1}})


    @staticmethod
    def insert_question(username, title, description):
        question = {
            "username": username,
            "title": title,
            "description": description,
            "answer_count": 0
        }
        mongo.db.questions.insert_one(question)

    
    @staticmethod
    def get_answer_count(question_id):
        count = Question.find_by_id(question_id)["answer_count"]
        return count


    @staticmethod
    def update_question(question_id, username, title, description):
        current_answer_count = Question.get_answer_count(question_id)
        submit = {
            "username": username,
            "title": title,
            "description": description,
            "answer_count": current_answer_count
        }
        mongo.db.questions.update_one({"_id": ObjectId(question_id)}, {"$set": submit})


    @staticmethod
    def delete_question(question_id):
        mongo.db.questions.delete_one({"_id": ObjectId(question_id)})
