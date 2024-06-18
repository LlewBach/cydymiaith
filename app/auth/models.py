from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# from bson.objectid import ObjectId
from app import mongo, login_manager


@login_manager.user_loader
def load_user(username):
    try:
        user_doc = mongo.db.users.find_one({"username": username})
        if user_doc:
            return User(username=user_doc["username"], password=user_doc["password"])
    except Exception as e:
        print(f"Error in load_user method: {e}")
    return None


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username.lower()
        self.password = password #need to rename password hash


    @classmethod
    def find_by_username(cls, username):
        """Retrieve a user from the database by username."""
        try:
            user = mongo.db.users.find_one({"username": username.lower()})
            if user:
                return cls(username=user['username'], password=user['password'])
        except Exception as e:
            print(f"Error in find_by_username method: {e}")
        return None

    
    @staticmethod
    def create_new(username, password):
        """Create a new user with a hashed password and store it in the database."""
        registrant = {
            "username": username.lower(),
            # can customize hash and salt methods, this standard
            # if second field to confirm password, would confirm before here
            "password": generate_password_hash(password)
        }
        try:
            mongo.db.users.insert_one(registrant)
            return User(username=username.lower(), password=password)
        except Exception as e:
            print(f"Error in create_new method: {e}")
            return None        


    def get_id(self):#
        return self.username


    def authenticate(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password, password)
