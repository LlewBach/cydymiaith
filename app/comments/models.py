from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo


class Comment:
    # Docstrings written by GPT4o and edited by myself.
    @staticmethod
    def find_by_id(comment_id):
        """
        Retrieves an answer from the database by its ID.

        This method queries the database to find a answer document that matches the provided answer ID.

        Args:
            answer_id (str): The ID of the question to be retrieved.

        Returns:
            dict: The answer document matching the provided ID, or None if an exception occurs.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            comment = mongo.db.comments.find_one({"_id": ObjectId(comment_id)})
            return comment
        except Exception as e:
            print(f"Error in find_by_id method: {e}")
            return None


    @staticmethod
    def find_comments_by_post_id(post_id):
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
            comments = list(mongo.db.comments.find({"post_id": ObjectId(post_id)}))
            for comment in comments:
                Comment.set_time_ago(comment)
            return comments
        except Exception as e:
            print(f"Error in find_comments_by_post_id method: {e}")
            return []
    

    @staticmethod
    def set_time_ago(comment):
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
            creation_time = comment['_id'].generation_time.replace(tzinfo=pytz.utc)
            comment['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def count_comments(comments):
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
            return len(comments)   
        except Exception as e:
            print(f"Error in count_comments method: {e}")
            return 0 
    

    @staticmethod
    def find_post_id(comment_id):
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
            post_id = mongo.db.comments.find_one({"_id": ObjectId(comment_id)})["post_id"]
            return post_id
        except Exception as e:
            print(f"Error in find_question_id method: {e}")
            return None
    

    @staticmethod
    def insert_comment(post_id, text, username):
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
            comment = {
                "post_id": ObjectId(post_id),
                "text": text,
                "username": username
            }
            mongo.db.comments.insert_one(comment)
        except Exception as e:
            print(f"Error in insert_comment method: {e}")


    @staticmethod
    def edit_comment(comment_id, post_id, text, username):
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
            comment = {
                "post_id": post_id,
                "text": text,
                "username": username
            }
            mongo.db.comments.update_one({"_id": ObjectId(comment_id)}, {"$set": comment})
        except Exception as e:
            print(f"Error in edit_comment method: {e}")

    
    @staticmethod
    def delete_comment(comment_id):
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
            mongo.db.comments.delete_one({"_id": ObjectId(comment_id)})
        except Exception as e:
            print(f"Error in delete_comment method: {e}")