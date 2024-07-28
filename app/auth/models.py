from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo, login_manager
from app.posts.models import Post
from app.comments.models import Comment


# Docstrings written by GPT4o and edited by myself.
@login_manager.user_loader
def load_user(username):
    """
    Loads a user from the database by username.

    This function is used by Flask-Login to retrieve a user object from the
    database based on the provided username. It is decorated with
    @login_manager.user_loader to indicate that it is the user loader callback
    function.

    Args:
        username (str): The username of the user to be loaded.

    Returns:
        User: A User object if the user is found in the database.
        None: If the user is not found or an exception occurs during the
        database query.
    """
    try:
        user_doc = mongo.db.users.find_one({"username": username})
        if user_doc:
            return User(
                username=user_doc["username"],
                password=user_doc["password"],
                role=user_doc["role"])

    except Exception as e:
        print(f"Error in load_user method: {e}")
        return None


class User(UserMixin):
    def __init__(self, username, password, role):
        """
        Initializes a User instance.

        Args:
            username (str): The username of the user.
            password (str): The password hash of the user.
            role (str): The role of the user (e.g., "Admin", "Student").

        Attributes:
            username (str): The username of the user.
            password (str): The password hash of the user.
            role (str): The role of the user.
        """
        self.username = username.lower()
        self.password = password
        self.role = role

    def set_password(self, new_password):
        """
        Hashes the new password and updates it in the database.

        This method takes a new password, hashes it using a secure hashing
        algorithm, updates the user's password attribute, and then saves the
        hashed password to the database.

        Args:
            new_password (str): The new password to be set for the user.

        Raises:
            Exception: If there is an issue with the database update, the
            exception is caught and an error message is printed.
        """
        new_password_hash = generate_password_hash(new_password)
        self.password = new_password_hash
        try:
            mongo.db.users.update_one(
                {"username": self.username},
                {"$set": {"password": new_password_hash}}
            )

        except Exception as e:
            print(f'Error in set_password method: {e}')

    @classmethod
    def find_by_email(cls, email):
        """
        Finds a user by their email address.

        This method queries the database for a user document with the specified
        email address. If a user is found, it returns an instance of the User
        class. If no user is found or an exception occurs, it returns None.

        Args:
            email (str): The email address of the user to be found.

        Returns:
            User: An instance of the User class if a user with the specified
            email is found.
            None: If no user is found or an exception occurs during the
            database query.

        Raises:
            Exception: If there is an issue with the database query, the
            exception is caught and an error message is printed, returning
            None.
        """
        try:
            user_doc = mongo.db.users.find_one({"email": email})
            if user_doc:
                return cls(
                    username=user_doc['username'],
                    password=user_doc['password'],
                    role=user_doc['role']
                    )
            else:
                return None
        except Exception as e:
            print(f"Error in find_by_email method: {e}")
            return None

    @classmethod
    def find_by_username(cls, username, as_dict=False):
        """
        Retrieves a user from the database by username.

        This method queries the database for a user document with the specified
        username. If a user is found, it returns an instance of the User class
        or a dictionary representation of the user depending on the value of
        the as_dict parameter. If no user is found or an exception occurs, it
        returns None.

        Args:
            username (str): The username of the user to be found.
            as_dict (bool, optional): If True, returns the user as a
            dictionary. Defaults to False.

        Returns:
            User: An instance of the User class if a user with the specified
            username is found and as_dict is False.
            dict: A dictionary representation of the user if as_dict is True.
            None: If no user is found or an exception occurs during the
            database query.

        Raises:
            Exception: If there is an issue with the database query, the
            exception is caught and an error message is printed, returning
            None.
        """
        try:
            user = mongo.db.users.find_one({"username": username.lower()})
            if user:
                if as_dict:
                    return user
                else:
                    return cls(
                        username=user['username'],
                        password=user['password'],
                        role=user['role']
                        )
        except Exception as e:
            print(f"Error in find_by_username method: {e}")
        return None

    @staticmethod
    def create_new(username, password, email):
        """
        Creates a new user with a hashed password and stores it in the
        database.

        This method takes a username, password, and email, hashes the password,
        and creates a new user document with a default role of "Student". It
        then inserts this document into the database. If the insertion is
        successful, it returns an instance of the User class representing the
        new user.

        Args:
            username (str): The username of the new user.
            password (str): The plain text password of the new user.
            email (str): The email address of the new user.

        Returns:
            User: An instance of the User class representing the new user.
            None: If there is an issue with the database insertion.

        Raises:
            Exception: If there is an issue with the database insertion, the
            exception is caught and an error message is printed, returning
            None.
        """
        registrant = {
            "email": email,
            "username": username.lower(),
            "password": generate_password_hash(password),
            "role": "Student",
            "level": "",
            "provider": "",
            "location": "",
            "bio": ""
        }
        try:
            mongo.db.users.insert_one(registrant)
            return User(
                username=username.lower(),
                password=password,
                role=None
                )
        except Exception as e:
            print(f"Error in create_new method: {e}")
            return None

    def get_id(self):
        """
        Returns the unique identifier for the user.

        This method is used by Flask-Login to get the unique identifier for the
        user. In this case, the username is used as the unique identifier.

        Returns:
            str: The username of the user.
        """
        return self.username

    def authenticate(self, password):
        """
        Verifies the provided password against the stored password hash.

        This method checks if the provided plain text password matches the
        hashed password stored for the user.

        Args:
            password (str): The plain text password to verify.

        Returns:
            bool: True if the provided password matches the stored hash, False
            otherwise.
        """
        return check_password_hash(self.password, password)

    @staticmethod
    def update_profile(email, username, role, level, provider, location, bio):
        """
        Updates a user's profile in the database.

        This static method updates the profile information of a user in the
        database. It retrieves the existing user by username, retains the
        current password, and updates the profile fields with the provided
        values. If the role is not specified, it retains the current role of
        the user.

        Args:
            email (str): The new email address of the user.
            username (str): The username of the user whose profile is to be
            updated.
            role (str): The new role of the user. If not provided, retains the
            current role.
            level (str): The new level of the user.
            provider (str): The new provider of the user.
            location (str): The new location of the user.
            bio (str): The new bio of the user.

        Raises:
            Exception: If there is an issue with the database update, the
            exception is caught and an error message is printed.
        """
        try:
            user = User.find_by_username(username)
            password = user.password
            if role:
                designated_role = role
            else:
                designated_role = user.role
            profile = {
                "email": email,
                "username": username,
                "password": password,
                "role": designated_role,
                "level": level,
                "provider": provider,
                "location": location,
                "bio": bio
            }
            mongo.db.users.update_one(
                {"username": user.username},
                {"$set": profile}
                )
        except Exception as e:
            print(f"Error in update_profile method: {e}")

    @staticmethod
    def delete_profile(username):
        """
        Deletes a user's profile and associated data from the database.

        This static method deletes a user's profile from the database, along
        with all answers and questions associated with the user. It first
        deletes the user's answers, updates the answer count of the related
        questions, then deletes the user's questions and all associated
        answers, and finally deletes the user's profile.

        Args:
            username (str): The username of the user whose profile is to be
            deleted.

        Raises:
            Exception: If there is an issue with the database operations, the
            exception is caught and an error message is printed.
        """
        try:
            comments_to_delete = list(mongo.db.comments
                                      .find({"username": username}))
            for comment in comments_to_delete:
                comment_id = comment["_id"]
                post_id = Comment.find_post_id(comment_id)
                Post.decrease_comment_count(post_id)
                Comment.delete_comment(comment_id)

            posts_to_delete = list(mongo.db.posts.find({"username": username}))
            for post in posts_to_delete:
                post_id = post["_id"]
                mongo.db.comments.delete_many({"post_id": post_id})
                mongo.db.posts.delete_one({"_id": post_id})

            mongo.db.groups.delete_many({"tutor": username})

            mongo.db.users.delete_one({"username": username})
        except Exception as e:
            print(f"Error in delete_profile method: {e}")

    @staticmethod
    def get_users(level, provider, username, email, location):
        """
        Retrieves a list of users from the database based on the provided
        filters.

        This static method queries the database for user documents that match
        the provided filter criteria. It constructs a query based on the
        non-None parameters and returns the list of users that match the query.
        If no filters are provided, it returns all users.

        Args:
            level (str): The level of the users to be retrieved.
            provider (str): The provider of the users to be retrieved.
            username (str): The username of the users to be retrieved.
            email (str): The email address of the user to be retrieved.
            location (str): The location of the users to be retrieved.

        Returns:
            tuple: A tuple containing:
                - list: A list of user documents that match the query.
                - dict: The query dictionary used to filter the users. This is
                used to populate the html filter inputs.

        Raises:
            Exception: If there is an issue with the database query, the
            exception is caught and an error message is printed, returning
            None.
        """
        query = {}
        if level:
            query['level'] = level
        if provider:
            query['provider'] = provider
        if username:
            query['username'] = username
        if email:
            query['email'] = email
        if location:
            query['location'] = location
        try:
            if query:
                users = list(mongo.db.users.find(query))
            else:
                users = list(mongo.db.users.find())
            return users, query
        except Exception as e:
            print(f"Error in get_users method: {e}")
            return None
