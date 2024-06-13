from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from app import mongo


auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("auth.login"))
        
        register = {
            "username": request.form.get("username").lower(),
            # can customize hash and salt methods, this standard
            # if second field to confirm password, would confirm before here
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profiles.profile", username=session["user"]))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Croeso, {}".format(request.form.get("username")))
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