from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.auth.models import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = User.find_by_username(request.form.get("username"))
        
        if existing_user:
            flash("Username already exists")    
            return redirect(url_for("auth.login"))
        
        username = request.form.get("username").lower()
        password = request.form.get("password")
        User.create_new(username, password)
        session["user"] = username
        flash("Registration Successful!")
        return redirect(url_for("profiles.profile", username=session["user"]))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = User.find_by_username(request.form.get("username"))
        
        if existing_user:
            given_password = request.form.get("password")
            if existing_user.authenticate(given_password):
                session["user"] = existing_user.username
                flash("Croeso, {}".format(session["user"]))
                return redirect(url_for(
                    "profiles.profile", username=session["user"]))
            else:
                flash("Incorrect username and/or password")
                return redirect(url_for('auth.login'))
            
        else:
            flash("Incorrect username and/or password")
            return redirect(url_for('auth.login'))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    flash("Logged out")
    session.pop("user")
    return redirect(url_for("auth.login"))