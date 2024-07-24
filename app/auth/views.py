from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import mail
from app.auth.models import User
from app.questions.models import Question
from app.groups.models import Group

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@auth_bp.route('/send_confirmation/<email>')
def send_confirmation(email):
    """
    Sends a password reset confirmation email to the specified email address.

    This function generates a secure token using the email address and the application's
    secret key. It then constructs a password reset URL containing the token and sends
    an email with this URL to the specified email address. A success message is flashed
    to the user and the user is redirected to their profile page.

    Args:
    email (str): The email address to which the confirmation email will be sent.

    Returns:
    A redirect response to the user's profile page.
    """
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
    """
    Resets user's password using a token sent via email.

    Verifies the token provided in the URL to reset user's password.
    If token is valid, it allows the user to set a new password. If the token is 
    expired or invalid, it flashes an appropriate error message and redirects to the 
    login page.

    Args:
        token (str): The token used to verify the password reset request.

    Returns:
        Response: Renders the password reset template on GET requests.
        Response: Redirects to the login page if the token is invalid or expired.
        Response: Redirects to the user's profile page after successfully resetting the password.
    """
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


@auth_bp.route('/reg_confirmation', methods=['GET', 'POST'])
def reg_confirmation():
    """
    Handles the email confirmation process for user registration.

    On GET requests, it renders a form where users can enter their email address
       to receive a confirmation link for registration.
    
    On POST requests, it generates a secure token using the provided email address
       and the application's secret key. It then constructs a confirmation URL containing
       the token and sends an email with this URL to the specified email address. A success
       message is flashed to the user and the user is redirected back to the confirmation page.

    Returns:
        Response: Renders the email confirmation form template on GET requests.
        Response: Redirects to same page with a success message on POST requests.
    """
    if request.method == 'POST':
        email = request.form.get("reg_email")
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='reg-confirmation-salt')
        confirmation_url = url_for('auth.register', token=token, _external=True)
        msg = Message("Confirm email address to register", recipients=[email])
        msg.body = f"To confirm email, please visit the following link: {confirmation_url}"
        mail.send(msg)
        flash('A confirmation email has been sent.', 'success')
        return redirect(url_for('auth.reg_confirmation'))
    
    return render_template('reg_email.html')


@auth_bp.route("/register/<token>", methods=["GET", "POST"])
def register(token):
    """
    Handles the user registration process.

    This function processes user registration through an email confirmation link. It verifies 
    the provided token to confirm the email address. If the token is valid and the user is 
    not authenticated, it renders a registration form on GET requests. On POST requests, 
    it attempts to register the user with the provided username and password.

    Args:
        token (str): The token used to verify the email confirmation request.

    Returns:
        Response: 
            - Renders the registration template on GET requests.
            - Redirects to the email confirmation page with an error message if the token is invalid or expired.
            - Redirects to the login page with an error message if the username already exists.
            - Redirects to the profile page with a success message after successful registration and login.
            - Redirects to the home page if the user is already authenticated.

    Raises:
        SignatureExpired: If the token has expired.
        BadSignature: If the token is invalid.
    """
    try:
        email = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(
            token, salt='reg-confirmation-salt', max_age=3600)
    except SignatureExpired:
        flash('The reset link has expired.', 'error')
        return redirect(url_for('auth.reg_confirmation'))
    except BadSignature:
        flash('The reset link is invalid.', 'error')
        return redirect(url_for('auth.reg_confirmation'))

    if current_user.is_authenticated:
        return redirect(url_for('core.home'))

    if request.method == "POST":
        existing_user = User.find_by_username(request.form.get("username"))
        if existing_user:
            flash("That username is already in use", "error")    
            return redirect(url_for("auth.login"))
        
        username = request.form.get("username").lower()
        password = request.form.get("password")
        user = User.create_new(username, password, email)
        login_user(user)
        flash("Registration Successful!", "success")
        return redirect(url_for("auth.profile", username=user.username))

    return render_template("register.html", token=token)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles the user login process.

    This function handles the GET and POST requests for user login. On a GET request,
    it renders the login template. On a POST request, it processes the login form data,
    verifies the username and password, logs the user in if the credentials are correct,
    and redirects them to their profile page.

    If the user is already authenticated, they are redirected to the questions page.

    Returns:
        Response: Renders the login template on GET requests.
        Response: Redirects to the questions page if the user is already authenticated.
        Response: Redirects to the profile page after successful login.
        Response: Redirects to the login page with an error message if the credentials are incorrect.
    """
    if current_user.is_authenticated:
        return redirect(url_for('questions.get_posts'))
    
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
                flash("Incorrect username and/or password", "error")
                return redirect(url_for('auth.login'))
            
        else:
            flash("Incorrect username and/or password", "error")
            return redirect(url_for('auth.login'))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Logs out the current user.

    This function logs out the currently authenticated user, flashes a logout success
    message, and redirects the user to the login page.

    Returns:
        Response: A redirect response to the login page after logging out the user.
    """
    logout_user()
    flash("Logged Out")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile/<username>")
@login_required
def profile(username):
    """
    Displays the profile page for the specified user.

    This function retrieves the user's profile information and their associated questions
    based on the provided username. It then renders the profile page template with this data.

    Args:
        username (str): The username of the user whose profile is to be displayed.

    Returns:
        Response: Renders the profile template with the user's information and questions.
    """
    questions = Question.get_list_by_username(username)
    user = User.find_by_username(username, True)

    return render_template("profile.html", user=user, questions=questions)


def user_owns_profile_or_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        username = kwargs.get('username')
        if current_user.username != username and current_user.role != "Admin":
            flash("You are not authorized to do this.", "error")
            return redirect(url_for('auth.profile', username=current_user.username))
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route("/edit_profile/<username>", methods=["GET", "POST"])
@login_required
@user_owns_profile_or_admin
def edit_profile(username):
    """
    Handles the editing of a user's profile.

    On a POST request, it updates the user's profile with the provided data.

    The function prevents the submission of an email address that is already in use.

    Only the profile owner or an Admin can edit the profile.

    Args:
        username (str): The username of the user whose profile is to be edited.

    Returns:
        Response: Renders the edit_profile template on GET requests.
        Response: Redirects to the edit_profile page if the email address is already in use.
        Response: Redirects to the user's profile page after successful profile update.
        Response: Redirects to the users view page if the current user is an Admin.
        Response: Redirects to the current user's profile page if they are not authorized to edit the profile.
    """
    
    if request.method == "POST":
        email = request.form.get("email")
        found_user = User.find_by_email(email)
        if found_user.username != username:
            flash("That email is already in use")
            return redirect(url_for('auth.profile', username=current_user.username))
        role = request.form.get("role")
        level = request.form.get("level")
        provider = request.form.get("provider")
        location = request.form.get("location")
        bio = request.form.get("bio")
        User.update_profile(email, username, role, level, provider, location, bio)
        flash("Profile Updated", "success")
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
@user_owns_profile_or_admin
def delete_profile(username):
    """
    Deletes a user's profile.

    Verifies if the current user is authorized to delete the profile (either the profile owner or an Admin). If authorized, 
    it deletes the user's profile, flashes a success message, and redirects accordingly.

    Args:
        username (str): The username of the user whose profile is to be deleted.

    Returns:
        Response: Redirects to the current user's profile page if they are not authorized to delete the profile.
        Response: Redirects to the users view page if the current user is an Admin.
        Response: Redirects to the login page after successful profile deletion if the current user is not an Admin.
    """
    
    User.delete_profile(username)
    flash("Account Deleted")
    if current_user.role == "Admin":
        return redirect(url_for("auth.view_users"))
    else:
        logout_user()
        return redirect(url_for("auth.login"))


@auth_bp.route("/view_users", methods=["GET", "POST"])
@login_required
def view_users():
    """
    Displays and filters the list of users.

    On a GET request, it retrieves all users and renders the users view template. 
    On a POST request, it filters the users based on the provided form data (level, provider, username, email, location) 
    and then renders the users view template with the filtered results.

    Returns:
        Response: Renders the users view template with the list of users and additional context data.
    """
    if current_user.role == 'Student':
        flash("Unauthorized")
        return redirect(url_for("auth.profile", username=current_user.username))

    users, query = User.get_users(None, None, None, None, None)

    if request.method == 'POST':
        level = request.form.get('level')
        provider = request.form.get('provider')
        username = request.form.get('username')
        email = request.form.get('email')
        location = request.form.get('location')
        users, query = User.get_users(level, provider, username, email, location)
    
    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    levels = User.get_levels()
    providers = User.get_providers()

    return render_template("users.html", users=users, query=query, groups=groups, levels=levels, providers=providers)

