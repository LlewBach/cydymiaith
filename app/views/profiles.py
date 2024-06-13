from flask import Blueprint, render_template, session, redirect, url_for
# from app import mongo
from app.models.user import User

profiles_bp = Blueprint('profiles', __name__, template_folder='../templates')

@profiles_bp.route("/profile/<username>")
def profile(username):
    username = User.find_by_username(username).username
    
    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))