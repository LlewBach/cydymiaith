from flask import Flask
from flask_pymongo import PyMongo
import os

if os.path.exists("env.py"):
    import env

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.secret_key = os.environ.get("SECRET_KEY")

    mongo.init_app(app)

    from .auth.views import auth_bp
    from .questions.views import questions_bp
    from .profiles.views import profiles_bp
    from .answers.views import answers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(answers_bp)

    
    # app.mongo = mongo

    return app