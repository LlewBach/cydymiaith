from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo


class Answer:
    @staticmethod
    def find_answers_by_question_id(question_id):
        """
        Retrieve answers from the database associated with the question_id.

        To each answer, add a time_ago property.
        """
        try:
            answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
            for answer in answers:
                Answer.set_time_ago(answer)
            return answers
        except Exception as e:
            print(f"Error in find_answers_by_question_id method: {e}")
            return []
    

    @staticmethod
    def set_time_ago(answer):
        """
        Finds the time that an answer was created based on generated id.

        Subtracts creation time from current time.

        Uses humanize to create a readable time_ago figure.

        Sets the answer's time_ago property.
        """
        try:
            creation_time = answer['_id'].generation_time.replace(tzinfo=pytz.utc)
            answer['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def count_answers(answers):
        """
        Returns the length of the passed answers list.
        """
        try:
            return len(answers)   
        except Exception as e:
            print(f"Error in count_answers method: {e}")
            return 0 
    

    @staticmethod
    def find_question_id(answer_id):
        """
        Returns the id of the question associated with a certain answer.
        """
        try:
            question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]
            return question_id
        except Exception as e:
            print(f"Error in find_question_id method: {e}")
            return None
    

    @staticmethod
    def insert_answer(question_id, text, username):
        """
        Inserts an answer into the answers collection.
        """
        try:
            answer = {
                "question_id": ObjectId(question_id),
                "text": text,
                "username": username
            }
            mongo.db.answers.insert_one(answer)
        except Exception as e:
            print(f"Error in insert_answer method: {e}")


    @staticmethod
    def edit_answer(answer_id, question_id, text, username):
        """
        Updates an answer in the database.
        """
        try:
            answer = {
                "question_id": question_id,
                "text": text,
                "username": username
            }
            mongo.db.answers.update_one({"_id": ObjectId(answer_id)}, {"$set": answer})
        except Exception as e:
            print(f"Error in edit_answer method: {e}")

    
    @staticmethod
    def delete_answer(answer_id):
        """
        Deletes an answer from the database.
        """
        try:
            mongo.db.answers.delete_one({"_id": ObjectId(answer_id)})
        except Exception as e:
            print(f"Error in delete_answer method: {e}")