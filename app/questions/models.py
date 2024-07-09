from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo

class Question:
    # Docstrings written by GPT4o and edited by myself.
    @staticmethod
    def get_categories():
        """
        Retrieves the list of categories from the database.

        This method queries the database to retrieve all category documents from the categories collection and returns them as a list.

        Returns:
            list: A list of category documents from the categories collection. If an exception occurs, returns an empty list.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            categories = list(mongo.db.categories.find())
            return categories
        except Exception as e:
            print(f"Error in get_categories method: {e}")
            return []


    @staticmethod
    def find_by_id(question_id):
        """
        Retrieves a question from the database by its ID.

        This method queries the database to find a question document that matches the provided question ID.

        Args:
            question_id (str): The ID of the question to be retrieved.

        Returns:
            dict: The question document matching the provided ID, or None if an exception occurs.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
            return question
        except Exception as e:
            print(f"Error in find_by_id method: {e}")
            return None

    
    @staticmethod
    def get_list(category, group_id):
        """
        Retrieves a list of questions from the database filtered by category and/or group.

        This method queries the database to find questions that match the provided category and/or group ID.
        If neither category nor group ID is provided, it retrieves all questions. The questions are sorted
        in descending order by their ID. For each question, it calculates and adds the time_ago property.

        Args:
            category (str, optional): The category to filter questions by.
            group_id (str, optional): The group ID to filter questions by.

        Returns:
            list: A list of question documents matching the provided filters, with the time_ago property added.
            If an exception occurs, returns an empty list.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            query = {}
            if category:
                query['category'] = category
            if group_id:
                query['group_id'] = group_id
            if query:
                questions = list(mongo.db.questions.find(query).sort("_id", -1))
            else:
                questions = list(mongo.db.questions.find().sort("_id", -1))
            for question in questions:
                Question.set_time_ago(question)
            return questions
        except Exception as e:
            print(f"Error in get_list method: {e}")
            return []
        

    @staticmethod
    def get_list_by_username(username):
        """
        Retrieves a list of questions from the database associated with a specific username.

        This method queries the database to find all questions that are associated with the provided username.
        The questions are sorted in descending order by their ID. For each question, it calculates and adds
        the time_ago property.

        Args:
            username (str): The username to filter questions by.

        Returns:
            list: A list of question documents associated with the provided username, with the time_ago property added.
            If an exception occurs, returns an empty list.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            questions = list(mongo.db.questions.find({"username": username}).sort("_id, -1"))
            for question in questions:
                Question.set_time_ago(question)
            return questions
        except Exception as e:
            print(f"Error in get_list_by_username method: {e}")
            return []
    

    @staticmethod
    def set_time_ago(question):
        """
        Calculates and sets the 'time_ago' property for a question based on its creation time.

        This method calculates the creation time of the question using the generation time of its ID.
        It then computes the 'time_ago' property using the humanize library to provide a human-readable
        relative time (e.g., "3 days ago").

        Args:
            question (dict): The question document for which the 'time_ago' property will be calculated and set.

        Raises:
            Exception: If there is an issue with calculating the 'time_ago' property, the exception is caught and an error message is printed.
        """
        try:
            creation_time = question['_id'].generation_time.replace(tzinfo=pytz.utc)
            question['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def increase_answer_count(question_id):
        """
        Increases the answer_count property of a question by one.

        This method updates the specified question in the database, incrementing its answer_count property by one.

        Args:
            question_id (str): The ID of the question whose answer_count is to be increased.

        Raises:
            Exception: If there is an issue with updating the question in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': 1}})
        except Exception as e:
            print(f"Error in increase_answer_count method: {e}")


    @staticmethod
    def decrease_answer_count(question_id):
        """
        Decreases the answer_count property of a question by one.

        This method updates the specified question in the database, decrementing its answer_count property by one.

        Args:
            question_id (str): The ID of the question whose answer_count is to be decreased.

        Raises:
            Exception: If there is an issue with updating the question in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': -1}})
        except Exception as e:
            print(f"Error in decrease_answer_count method: {e}")


    @staticmethod
    def insert_question(username, category, group_id, title, description):
        """
        Inserts a new question into the database.

        This method creates a question document with the provided username, category, group ID,
        title, and description, and inserts it into the questions collection in the database.
        The answer_count is initialized to 0.

        Args:
            username (str): The username of the user creating the question.
            category (str): The category of the question.
            group_id (str): The ID of the group associated with the question.
            title (str): The title of the question.
            description (str): The description of the question.

        Raises:
            Exception: If there is an issue with inserting the question into the database, the exception
            is caught and an error message is printed.
        """
        try:
            question = {
                "username": username,
                "category": category,
                "group_id": group_id,
                "title": title,
                "description": description,
                "answer_count": 0
            }
            mongo.db.questions.insert_one(question)
        except Exception as e:
            print(f"Error in insert_question method: {e}")

    
    @staticmethod
    def get_answer_count(question_id):
        """
        Retrieves the answer_count associated with a specific question.

        This method queries the database to find the question by its ID and returns its answer_count property.

        Args:
            question_id (str): The ID of the question whose answer_count is to be retrieved.

        Returns:
            int: The answer_count of the question. If an exception occurs, returns 0.

        Raises:
            Exception: If there is an issue with retrieving the question from the database, the exception is caught and an error message is printed.
        """
        try:
            count = Question.find_by_id(question_id)["answer_count"]
            return count
        except Exception as e:
            print(f"Error in get_answer_count method: {e}")
            return 0


    @staticmethod
    def update_question(question_id, username, title, description):
        """
        Updates the details of a specific question in the database.

        This method updates the specified question in the database with the provided username, title, and description.
        The current answer_count is also retrieved and retained during the update.

        Args:
            question_id (str): The ID of the question to be updated.
            username (str): The username of the user updating the question.
            title (str): The updated title of the question.
            description (str): The updated description of the question.

        Raises:
            Exception: If there is an issue with updating the question in the database, the exception is caught and an error message is printed.
        """
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
            print(f"Error in update_question method: {e}")


    @staticmethod
    def delete_question(question_id):
        """
        Deletes a question and its associated answers from the database.

        This method deletes all answers associated with the specified question from the database,
        and then deletes the question itself.

        Args:
            question_id (str): The ID of the question to be deleted.

        Raises:
            Exception: If there is an issue with deleting the question or its associated answers from the database,
            the exception is caught and an error message is printed.
        """
        try:
            mongo.db.answers.delete_many({"question_id": ObjectId(question_id)})
            mongo.db.questions.delete_one({"_id": ObjectId(question_id)})
        except Exception as e:
            print(f"Error in delete_question method: {e}")
