from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo

class Answer:
    def __init__(self, question_id, text, username):
        self.question_id = question_id
        self.text = text
        self.username = username


    @staticmethod
    def find_answers_by_question_id(question_id):
        """Retrieve an answer from the database by question_id."""
        answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
        for answer in answers:
            Answer.set_time_ago(answer)
        return answers
    

    @staticmethod
    def set_time_ago(answer):
        creation_time = answer['_id'].generation_time.replace(tzinfo=pytz.utc)
        answer['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)

    
    @staticmethod
    def count_answers(answers):
        return len(answers)    
    

    @staticmethod
    def find_question_id(answer_id):
        question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]
        return question_id
    

    @staticmethod
    def insert_answer(question_id, text, username):
        answer = {
            "question_id": ObjectId(question_id),
            "text": text,
            "username": username
        }
        mongo.db.answers.insert_one(answer)


    @staticmethod
    def edit_answer(answer_id, question_id, text, username):
        answer = {
            "question_id": question_id,
            "text": text,
            "username": username
        }
        mongo.db.answers.update_one({"_id": ObjectId(answer_id)}, {"$set": answer})

    
    @staticmethod
    def delete_answer(answer_id):
        mongo.db.answers.delete_one({"_id": ObjectId(answer_id)})