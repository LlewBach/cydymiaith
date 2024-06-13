from flask import Blueprint, render_template, session, redirect, url_for

from app import mongo

profiles_bp = Blueprint('profiles', __name__, template_folder='../templates')

@profiles_bp.route("/profile/<username>")
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))