from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required
from app.auth.models import User

profiles_bp = Blueprint('profiles', __name__, template_folder='../templates')

@profiles_bp.route("/profile/<username>")
@login_required
def profile(username):
    username = User.find_by_username(username).username

    return render_template("profile.html", username=username)
    