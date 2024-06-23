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
        login_user(user)
        flash("Registration Successful!")
        return redirect(url_for("auth.profile", username=user.username))

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
                login_user(existing_user)
                flash("Croeso, {}".format(existing_user.username))
                return redirect(url_for(
                    "auth.profile", username=existing_user.username))
            else:
                flash("Incorrect username and/or password1")
                return redirect(url_for('auth.login'))
            
        else:
            flash("Incorrect username and/or password2")
            return redirect(url_for('auth.login'))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile/<username>")
@login_required
def profile(username):
    # if current_user.username != username:
    #     flash(f"You are not authorized to view this profile, {current_user.username}.")
    #     return redirect(url_for('auth.profile', username=current_user.username))
    
    user = User.find_by_username(username, True)
    return render_template("profile.html", user=user)


@auth_bp.route("/edit_profile/<username>", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    if current_user.username != username:
        flash(f"You are not authorized to view this profile, {current_user.username}.") # make into own function?
        return redirect(url_for('auth.profile', username=current_user.username))
    
    if request.method == "POST":
        level = request.form.get("level")
        provider = request.form.get("provider")
        location = request.form.get("location")
        bio = request.form.get("bio")
        User.update_profile(username, level, provider, location, bio)
        flash("Profile updated")
        return redirect(url_for('auth.profile', username=username))

    user = User.find_by_username(username, True)
    levels = User.get_levels()
    providers = User.get_providers()

    return render_template("edit_profile.html", user=user, levels=levels, providers=providers) 


@auth_bp.route("/delete_profile/<username>")
@login_required
def delete_profile(username):
    if current_user.username != username:
        flash(f"You are not authorized to do this, {current_user.username}.") # make into own function?
        return redirect(url_for('auth.profile', username=current_user.username))
    
    User.delete_profile(username)
    logout_user()
    flash("Account Deleted")
    return redirect(url_for("auth.login"))

