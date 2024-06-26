from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# from bson.objectid import ObjectId
from app import mongo, login_manager
from app.questions.models import Question
from app.answers.models import Answer


@login_manager.user_loader
def load_user(username):
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
        self.username = username.lower()
        self.password = password #need to rename password hash
        self.role = role

    
    def set_password(self, new_password):
        """
        Hash the new password and update it in the database.
        """
        new_password_hash = generate_password_hash(new_password)
        self.password = new_password_hash
        mongo.db.users.update_one(
            {"username": self.username},
            {"$set": {"password": new_password_hash}}
        )


    @staticmethod #Should be class method?
    def find_by_email(email):
        user_doc = mongo.db.users.find_one({"email": email})
        if user_doc:
            return User(username=user_doc['username'], password=user_doc['password'], role=user_doc['role'])
        return None


    @classmethod
    def find_by_username(cls, username, as_dict=False):
        """Retrieve a user from the database by username."""
        try:
            user = mongo.db.users.find_one({"username": username.lower()})
            if user:
                if as_dict:
                    return user
                else:
                    return cls(username=user['username'], password=user['password'], role=user['role'])
        except Exception as e:
            print(f"Error in find_by_username method: {e}")
        return None

    
    @staticmethod
    def create_new(username, password, email):
        """Create a new user with a hashed password and store it in the database."""
        registrant = {
            "email": email,
            "username": username.lower(),
            # can customize hash and salt methods, this standard
            # if second field to confirm password, would confirm before here
            "password": generate_password_hash(password),
            "role": None,
            "level": None,
            "provider": None,
            "location": None,
            "bio": None
        }
        try:
            mongo.db.users.insert_one(registrant)
            return User(username=username.lower(), password=password, role=None)
        except Exception as e:
            print(f"Error in create_new method: {e}")
            return None        


    def get_id(self):#
        return self.username


    def authenticate(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password, password)
    

    @staticmethod
    def get_roles():
        return list(mongo.db.roles.find())


    @staticmethod
    def get_levels():
        return list(mongo.db.levels.find())
    

    @staticmethod
    def get_providers():
        return list(mongo.db.providers.find())


    @staticmethod
    def update_profile(email, username, role, level, provider, location, bio):
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
        mongo.db.users.update_one({"username": user.username}, {"$set": profile})


    @staticmethod
    def delete_profile(username):
        answers_to_delete = list(mongo.db.answers.find({"username": username}))
        for answer in answers_to_delete:
            answer_id = answer["_id"]
            question_id = Answer.find_question_id(answer_id)
            Question.decrease_answer_count(question_id)
            Answer.delete_answer(answer_id)

        questions_to_delete = list(mongo.db.questions.find({"username": username}))
        for question in questions_to_delete:
            question_id = question["_id"]
            mongo.db.answers.delete_many({"question_id": question_id})
            mongo.db.questions.delete_one({"_id": question_id})            

        mongo.db.users.delete_one({"username": username})

    
    @staticmethod
    def get_users():
        users = list(mongo.db.users.find())
        return users