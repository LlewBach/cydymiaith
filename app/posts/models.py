from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo

class Post:
    # Docstrings written by GPT4o and edited by myself.
    @staticmethod
    def find_by_id(post_id):
        """
        Retrieves a post from the database by its ID.

        This method queries the database to find a post document that matches the provided post ID.

        Args:
            post_id (str): The ID of the post to be retrieved.

        Returns:
            dict: The post document matching the provided ID, or None if no post is found or if an exception occurs.

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
        Retrieves a list of posts from the database filtered by category and/or group.

        This method queries the database to find posts that match the provided category and/or group ID.
        If neither category nor group ID is provided, it retrieves all posts. The posts are sorted
        in descending order by their ID. For each post, it calculates and adds the time_ago property
        to enhance readability regarding when the post was created.

        Args:
            category (str, optional): The category to filter posts by.
            group_id (str, optional): The group ID to filter posts by.

        Returns:
            tuple:
                - list: A list of post documents matching the provided filters, each with the time_ago property added.
                - dict: The query dictionary used to retrieve the posts.
                If an exception occurs, returns an empty list and the query used.

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
        Retrieves a list of posts from the database associated with a specific username.

        This method queries the database to find all posts that are associated with the provided username.
        The posts are sorted in descending order by their ID to display the most recent posts first. For each post, 
        it calculates and adds the 'time_ago' property to provide context on how long ago the post was created.

        Args:
            username (str): The username to filter posts by. This is typically the author of the posts.

        Returns:
            list: A list of post documents associated with the provided username, each enhanced with the 'time_ago' property.
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
        Calculates and sets the 'time_ago' property for a post based on its creation time.

        This method calculates the creation time of the post using the generation time of its ID.
        It then computes the 'time_ago' property using the humanize library to provide a human-readable
        relative time (e.g., "3 days ago").

        Args:
            question (dict): The post document for which the 'time_ago' property will be calculated and set.

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
        Increases the comment_count property of a post by one.

        This method updates the specified post in the database, incrementing its comment_count property by one.

        Args:
            post_id (str): The ID of the post whose comment_count is to be increased.

        Raises:
            Exception: If there is an issue with updating the post in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'comment_count': 1}})
        except Exception as e:
            print(f"Error in increase_comment_count method: {e}")


    @staticmethod
    def decrease_comment_count(post_id):
        """
        Decreases the comment_count property of a post by one.

        This method updates the specified post in the database, decrementing its comment_count property by one.

        Args:
            post_id (str): The ID of the post whose comment_count is to be decreased.

        Raises:
            Exception: If there is an issue with updating the post in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'comment_count': -1}})
        except Exception as e:
            print(f"Error in decrease_comment_count method: {e}")


    @staticmethod
    def insert_post(username, category, group_id, title, description):
        """
        Inserts a new post into the database.

        This method creates a post document with the provided username, category, group ID,
        title, and description, and inserts it into the posts collection in the database.
        The comment_count is initialized to 0.

        Args:
            username (str): The username of the user creating the post.
            category (str): The category of the post.
            group_id (str): The ID of the group associated with the post.
            title (str): The title of the post.
            description (str): The description of the post.

        Raises:
            Exception: If there is an issue with inserting the post into the database, the exception
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
        Retrieves the comment_count associated with a specific post.

        This method queries the database to find the post by its ID and returns its comment_count property.

        Args:
            post_id (str): The ID of the post whose comment_count is to be retrieved.

        Returns:
            int: The comment_count of the post. If an exception occurs, returns 0.

        Raises:
            Exception: If there is an issue with retrieving the post from the database, the exception is caught and an error message is printed.
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
        Updates the details of a specific post in the database.

        This method updates the specified post in the database with the provided username, title, and description.
        The current comment_count is also retrieved and retained during the update.

        Args:
            post_id (str): The ID of the post to be updated.
            username (str): The username of the user updating the question.
            title (str): The updated title of the question.
            description (str): The updated description of the question.

        Raises:
            Exception: If there is an issue with updating the post in the database, the exception is caught and an error message is printed.
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
        Deletes a post and its associated comments from the database.

        This method deletes all comments associated with the specified post from the database,
        and then deletes the post itself.

        Args:
            post_id (str): The ID of the post to be deleted.

        Raises:
            Exception: If there is an issue with deleting the post or its associated comments from the database,
            the exception is caught and an error message is printed.
        """
        try:
            mongo.db.comments.delete_many({"post_id": ObjectId(post_id)})
            mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
        except Exception as e:
            print(f"Error in delete_post method: {e}")
