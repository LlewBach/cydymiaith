from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.models import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))#

    if request.method == "POST":
        existing_user = User.find_by_username(request.form.get("username"))
        
        if existing_user:
            flash("Username already exists")    
            return redirect(url_for("auth.login"))
        
        username = request.form.get("username").lower()
        password = request.form.get("password")
        user = User.create_new(username, password)
        # session["user"] = username
        login_user(user)
        flash("Registration Successful!")
        # return redirect(url_for("profiles.profile", username=session["user"]))
        return redirect(url_for("profiles.profile", username=user.username))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('questions.get_questions'))
    
    if request.method == "POST":
        existing_user = User.find_by_username(request.form.get("username"))
        
        if existing_user:
            given_password = request.form.get("password")
            if existing_user.authenticate(given_password):
                # session["user"] = existing_user.username
                login_user(existing_user)
                # flash("Croeso, {}".format(session["user"]))
                flash("Croeso, {}".format(existing_user.username))
                return redirect(url_for(
                    "profiles.profile", username=existing_user.username))
            else:
                flash("Incorrect username and/or password")
                return redirect(url_for('auth.login'))
            
        else:
            flash("Incorrect username and/or password")
            return redirect(url_for('auth.login'))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    # session.pop("user")
    return redirect(url_for("auth.login"))