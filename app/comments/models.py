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
        Retrieves a comment from the database by its ID.

        This method queries the database to find a comment document that matches the provided comment ID.

        Args:
            comment_id (str): The ID of the comment to be retrieved.

        Returns:
            dict: The comment document matching the provided ID, or None if not found or an error occurs.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed, returning None.
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
        Retrieves comments from the database associated with the given post ID and adds a time_ago property to each comment.

        This method queries the database for all comments associated with the specified post ID. For each comment retrieved, it adds a time_ago property to indicate how long ago the comment was posted. This helps provide context about the recency of comments when displaying them to users.

        Args:
            post_id (str): The ID of the post whose comments are to be retrieved.

        Returns:
            list: A list of comment documents, each with an added time_ago property. If an exception occurs, an empty list is returned.

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
        Calculates and sets the 'time_ago' property for a comment based on its creation time.

        This method extracts the creation time of the comment from its MongoDB ObjectId, calculates the time elapsed since its creation, and uses the 'humanize' library to generate a human-readable 'time_ago' description. It then sets this 'time_ago' value as a property of the comment document.

        Args:
            comment (dict): The comment document to update with a 'time_ago' property.

        Raises:
            Exception: If there is an issue with calculating or setting the 'time_ago' property, the exception is caught and an error message is printed. This ensures that the method gracefully handles errors while processing dates.
        """
        try:
            creation_time = comment['_id'].generation_time.replace(tzinfo=pytz.utc)
            comment['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
        except Exception as e:
            print(f"Error in set_time_ago method: {e}")

    
    @staticmethod
    def count_comments(comments):
        """
        Returns the number of comments in the provided list.

        This method calculates the length of the provided list of comments and returns it.
        If an exception occurs during the process, the method catches the exception, prints an error message, and returns 0. This ensures robust error handling during comment count operations.

        Args:
            comments (list): A list of comment documents to count.

        Returns:
            int: The number of comments in the provided list. Returns 0 if an exception occurs.

        Raises:
            Exception: If there is an issue with counting the comments, the exception is caught
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
        Retrieves the ID of the post associated with a given comment.

        This method queries the database to find the post ID associated with the specified comment ID.
        If an exception occurs, it catches the exception, prints an error message, and returns None.

        Args:
            comment_id (str): The ID of the comment for which the associated post ID is to be retrieved.

        Returns:
            str: The ID of the post associated with the given comment. Returns None if an exception occurs or if the comment does not exist or does not have an associated post ID.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught
            and an error message is printed, providing clear feedback for troubleshooting.
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
        Inserts a new comment into the comments collection in the database.

        This method creates a comment document with the provided post ID, comment text, and username,
        and inserts it into the comments collection in the database. If an exception occurs during this
        process, it catches the exception and prints an error message.

        Args:
            post_id (str): The ID of the post to which the comment is associated.
            text (str): The text content of the comment.
            username (str): The username of the user who provided the comment.

        Raises:
            Exception: If there is an issue with inserting the comment into the database, the exception
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
        Updates an existing comment in the database.

        This method updates the content of an existing comment in the database based on the provided comment ID.
        It sets the new post ID, text, and username for the comment. If an exception occurs, it catches the exception and prints an error message.

        Args:
            comment_id (str): The ID of the comment to be updated.
            post_id (str): The ID of the post to which the comment is associated.
            text (str): The updated text content of the comment.
            username (str): The username of the user who provided the comment.

        Raises:
            Exception: If there is an issue with updating the comment in the database, the exception
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
        Deletes a comment from the database.

        This method removes a comment from the database based on the provided comment ID.
        If an exception occurs, it catches the exception and prints an error message.

        Args:
            comment_id (str): The ID of the comment to be deleted.

        Raises:
            Exception: If there is an issue with deleting the comment from the database, the exception
            is caught and an error message is printed.
        """
        try:
            mongo.db.comments.delete_one({"_id": ObjectId(comment_id)})
        except Exception as e:
            print(f"Error in delete_comment method: {e}")