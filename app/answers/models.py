from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo


class Answer:
    # Docstrings written by GPT4o and edited by myself.
    @staticmethod
    def find_answers_by_question_id(question_id):
        """
        Retrieves answers from the database associated with the given question ID and adds a time_ago property to each answer.

        This method queries the database for all answers associated with the specified question ID. For each answer retrieved, it adds a time_ago property to indicate how long ago the answer was posted.

        Args:
            question_id (str): The ID of the question whose answers are to be retrieved.

        Returns:
            list: A list of answer documents, each with an added time_ago property. If an exception occurs, an empty list is returned.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught, an error message is printed, and an empty list is returned.
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
        Calculates and sets the time_ago property for an answer.

        This method determines the creation time of an answer based on its generated ID, calculates the difference between the creation time and the current time, and uses the humanize library to create a human-readable time_ago figure. It then
        sets this time_ago value as a property of the answer.

        Args:
            answer (dict): The answer document to update with a time_ago property.

        Raises:
            Exception: If there is an issue with calculating or setting the time_ago property,
            the exception is caught and an error message is printed.
        """
        try:
            creation_time = answer['_id'].generation_time.replace(tzinfo=pytz.utc)
            answer['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def count_answers(answers):
        """
        Returns the number of answers in the provided list.

        This method calculates the length of the provided list of answers and returns it. 
        If an exception occurs, it catches the exception, prints an error message, and returns 0.

        Args:
            answers (list): A list of answer documents to count.

        Returns:
            int: The number of answers in the provided list. Returns 0 if an exception occurs.

        Raises:
            Exception: If there is an issue with counting the answers, the exception is caught
            and an error message is printed.
        """
        try:
            return len(answers)   
        except Exception as e:
            print(f"Error in count_answers method: {e}")
            return 0 
    

    @staticmethod
    def find_question_id(answer_id):
        """
        Retrieves the ID of the question associated with a given answer.

        This method queries the database to find the question ID associated with the specified answer ID.
        If an exception occurs, it catches the exception, prints an error message, and returns None.

        Args:
            answer_id (str): The ID of the answer for which the associated question ID is to be retrieved.

        Returns:
            str: The ID of the question associated with the given answer. Returns None if an exception occurs.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught
            and an error message is printed.
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
        Inserts a new answer into the answers collection in the database.

        This method creates an answer document with the provided question ID, answer text, and username,
        and inserts it into the answers collection in the database. If an exception occurs, it catches
        the exception and prints an error message.

        Args:
            question_id (str): The ID of the question to which the answer is associated.
            text (str): The text content of the answer.
            username (str): The username of the user who provided the answer.

        Raises:
            Exception: If there is an issue with inserting the answer into the database, the exception
            is caught and an error message is printed.
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
        Updates an existing answer in the database.

        This method updates the content of an existing answer in the database based on the provided answer ID.
        It sets the new question ID, text, and username for the answer. If an exception occurs, it catches the exception and prints an error message.

        Args:
            answer_id (str): The ID of the answer to be updated.
            question_id (str): The ID of the question to which the answer is associated.
            text (str): The updated text content of the answer.
            username (str): The username of the user who provided the answer.

        Raises:
            Exception: If there is an issue with updating the answer in the database, the exception
            is caught and an error message is printed.
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

        This method removes an answer from the database based on the provided answer ID.
        If an exception occurs, it catches the exception and prints an error message.

        Args:
            answer_id (str): The ID of the answer to be deleted.

        Raises:
            Exception: If there is an issue with deleting the answer from the database, the exception
            is caught and an error message is printed.
        """
        try:
            mongo.db.answers.delete_one({"_id": ObjectId(answer_id)})
        except Exception as e:
            print(f"Error in delete_answer method: {e}")