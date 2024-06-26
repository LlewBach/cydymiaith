from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
import os

if os.path.exists("env.py"):
    import env

mongo = PyMongo()
# login_manager = LoginManager(app)
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    # MongoDB Configuration
    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.secret_key = os.environ.get("SECRET_KEY")

    # Flask-Mail Configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    # Initializing Extensions
    mongo.init_app(app)
    login_manager.init_app(app) #
    login_manager.login_view = 'auth.login'
    mail.init_app(app)

    from .core.views import core_bp
    from .auth.views import auth_bp
    from .questions.views import questions_bp
    # from .profiles.views import profiles_bp
    from .answers.views import answers_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    # app.register_blueprint(profiles_bp)
    app.register_blueprint(answers_bp)

    # @login_manager.user_loader
    # def load_user(user_id):
    #     from .auth.models import User
    #     return User.find_by_username(user_id)

    # app.mongo = mongo

    return app