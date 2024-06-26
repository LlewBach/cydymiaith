from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import mail
from app.auth.models import User
from app.questions.models import Question

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/send_confirmation/<email>')
def send_confirmation(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(email, salt='reset-password-salt')
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message("Password Reset Request", recipients=[email])
    msg.body = f"To reset your password, please visit the following link: {reset_url}"
    mail.send(msg)
    flash('A confirmation email has been sent.', 'success')
    return redirect(url_for('auth.profile', username=current_user.username))


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(
            token, salt='reset-password-salt', max_age=3600)
    except SignatureExpired:
        flash('The reset link has expired.', 'error')
        return redirect(url_for('auth.login'))
    except BadSignature:
        flash('The reset link is invalid.', 'error')
        return redirect(url_for('auth.login'))

    user = User.find_by_email(email)
    if not user:
        flash('No user found with this email address.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
            flash('Your password has been reset.', 'success')
            return redirect(url_for('auth.profile', username=current_user.username))
        else:
            flash('Password cannot be empty.', 'error')

    return render_template('reset_password.html', token=token)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))#

    if request.method == "POST":
        existing_user = User.find_by_username(request.form.get("username"))
        # also check for existing email
        if existing_user:
            flash("Username already exists")    
            return redirect(url_for("auth.login"))
        
        email = request.form.get("email")
        username = request.form.get("username").lower()
        password = request.form.get("password")
        user = User.create_new(username, password, email)
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
    questions = Question.get_list_by_username(username)
    user = User.find_by_username(username, True)
    return render_template("profile.html", user=user, questions=questions)


@auth_bp.route("/edit_profile/<username>", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    if current_user.username != username and current_user.role != "Admin":
        flash(f"You are not authorized to view this profile, {current_user.username}.") # make into own function?
        return redirect(url_for('auth.profile', username=current_user.username))
    
    if request.method == "POST":
        email = request.form.get("email")
        role = request.form.get("role")
        level = request.form.get("level")
        provider = request.form.get("provider")
        location = request.form.get("location")
        bio = request.form.get("bio")
        User.update_profile(email, username, role, level, provider, location, bio)
        flash("Profile updated")
        if current_user.role == "Admin":
            return redirect(url_for('auth.view_users'))
        else:
            return redirect(url_for('auth.profile', username=username))

    user = User.find_by_username(username, True)
    roles = User.get_roles()
    levels = User.get_levels()
    providers = User.get_providers()

    return render_template("edit_profile.html", user=user,roles=roles, levels=levels, providers=providers) 


@auth_bp.route("/delete_profile/<username>")
@login_required
def delete_profile(username):
    if current_user.username != username and current_user.role != "Admin":
        flash(f"You are not authorized to do this, {current_user.username}.") # make into own function?
        return redirect(url_for('auth.profile', username=current_user.username))
    
    User.delete_profile(username)
    if current_user.role == "Admin":
        return redirect(url_for("auth.view_users"))
    else:
        logout_user()
        flash("Account Deleted")
        return redirect(url_for("auth.login"))


@auth_bp.route("/view_users")
@login_required
def view_users():
    # if current_user.role not in ["Admin", "Tutor"]:
    #     flash(f"You are not authorized for this, {current_user.username}.") # make into own function?
    #     return redirect(url_for('auth.profile', username=current_user.username))
    
    users = User.get_users()
    return render_template("users.html", users=users)

