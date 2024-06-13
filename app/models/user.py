from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo

class User:
    def __init__(self, username, password):
        self.username = username.lower()
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        """Retrieve a user from the database by username."""
        user = mongo.db.users.find_one({"username": username.lower()})
        if user:
            return cls(username=user['username'], password=user['password'])
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
        mongo.db.users.insert_one(registrant)


    def authenticate(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password, password)
