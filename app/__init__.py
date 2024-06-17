from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
import os

if os.path.exists("env.py"):
    import env

mongo = PyMongo()
# login_manager = LoginManager(app)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.secret_key = os.environ.get("SECRET_KEY")

    mongo.init_app(app)
    login_manager.init_app(app) #
    login_manager.login_view = 'auth.login'

    from .core.views import core_bp
    from .auth.views import auth_bp
    from .questions.views import questions_bp
    from .profiles.views import profiles_bp
    from .answers.views import answers_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(answers_bp)

    # @login_manager.user_loader
    # def load_user(user_id):
    #     from .auth.models import User
    #     return User.find_by_username(user_id)

    # app.mongo = mongo

    return app