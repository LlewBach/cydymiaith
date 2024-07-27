from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo

class Post:
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
    def find_by_id(post_id):
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
            post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
            return post
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
        query = {}
        if category:
            query['category'] = category
        if group_id:
            query['group_id'] = group_id
        try:
            if query:
                posts = list(mongo.db.posts.find(query).sort("_id", -1))
            else:
                posts = list(mongo.db.posts.find().sort("_id", -1))
            for post in posts:
                Post.set_time_ago(post)
            return posts, query
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
            posts = list(mongo.db.posts.find({"username": username}).sort("_id, -1"))
            for post in posts:
                Post.set_time_ago(post)
            return posts
        except Exception as e:
            print(f"Error in get_list_by_username method: {e}")
            return []
    

    @staticmethod
    def set_time_ago(post):
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
            creation_time = post['_id'].generation_time.replace(tzinfo=pytz.utc)
            post['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def increase_comment_count(post_id):
        """
        Increases the answer_count property of a question by one.

        This method updates the specified question in the database, incrementing its answer_count property by one.

        Args:
            question_id (str): The ID of the question whose answer_count is to be increased.

        Raises:
            Exception: If there is an issue with updating the question in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'comment_count': 1}})
        except Exception as e:
            print(f"Error in increase_comment_count method: {e}")


    @staticmethod
    def decrease_comment_count(post_id):
        """
        Decreases the answer_count property of a question by one.

        This method updates the specified question in the database, decrementing its answer_count property by one.

        Args:
            question_id (str): The ID of the question whose answer_count is to be decreased.

        Raises:
            Exception: If there is an issue with updating the question in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'comment_count': -1}})
        except Exception as e:
            print(f"Error in decrease_comment_count method: {e}")


    @staticmethod
    def insert_post(username, category, group_id, title, description):
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
            post = {
                "username": username,
                "category": category,
                "group_id": group_id,
                "title": title,
                "description": description,
                "comment_count": 0
            }
            mongo.db.posts.insert_one(post)
        except Exception as e:
            print(f"Error in insert_post method: {e}")

    
    @staticmethod
    def get_comment_count(post_id):
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
            count = Post.find_by_id(post_id)["comment_count"]
            return count
        except Exception as e:
            print(f"Error in get_comment_count method: {e}")
            return 0


    @staticmethod
    def update_post(post_id, username, category, group_id, title, description):
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
            current_comment_count = Post.get_comment_count(post_id)
            submit = {
                "username": username,
                "category": category,
                "group_id": group_id,
                "title": title,
                "description": description,
                "comment_count": current_comment_count
            }
            mongo.db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": submit})
        except Exception as e:
            print(f"Error in update_question method: {e}")


    @staticmethod
    def delete_post(post_id):
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
            mongo.db.comments.delete_many({"post_id": ObjectId(post_id)})
            mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
        except Exception as e:
            print(f"Error in delete_post method: {e}")
