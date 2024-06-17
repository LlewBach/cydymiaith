from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
# from app.auth.models import User

profiles_bp = Blueprint('profiles', __name__, template_folder='../templates')

@profiles_bp.route("/profile/<username>")
@login_required
def profile(username):
    if current_user.username != username:
        flash("You are not authorized to view this profile.")
        return redirect(url_for('profiles.profile', username=current_user.username))

    return render_template("profile.html", username=username)
    