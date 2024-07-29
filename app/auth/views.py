from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, \
    flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import mail
from app.core.models import Core
from app.auth.models import User
from app.posts.models import Post
from app.groups.models import Group

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@auth_bp.route("/send_confirmation", defaults={"email": None})
@auth_bp.route('/send_confirmation/<email>')
def send_confirmation(email):
    """
    Sends a password reset confirmation email to the specified email address.

    This function checks if an email is provided. If an email is present, it:
      1. Generates a secure token using the email address and the application's
      secret key.
      2. Constructs a URL for password reset using the token.
      3. Sends an email with a password reset link to the specified email
      address.
      4. Flashes a success message to the user.
    If no email is provided, it flashes an error message.
    After the actions, it redirects the user either to the login page (on
    success) or to the home page (if email is not provided).

    Args:
        email (str, optional): The email address to which the confirmation
        email will be sent.

    Returns:
        Response: A redirect response to either the login page or the home
        page, based on the input.
    """
    if email:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='reset-password-salt')
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        msg = Message("Password Reset Request", recipients=[email])
        msg.body = (
            f"To reset your password, please visit the following link: "
            f"{reset_url}"
        )
        mail.send(msg)
        flash('A confirmation email has been sent.', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash("Email Not Specified")
        return redirect(url_for("core.home"))


@auth_bp.route('/reset_password', defaults={"token": None})
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Resets a user's password using a token sent via email.

    This function handles both GET and POST requests:
      - For GET requests, it renders a password reset template if the token is
      valid.
      - For POST requests, it processes the new password submission:
        - If the token is valid and the new password meets criteria, updates
        the user's password.
        - If the new password is empty, it flashes an error message.
    The function verifies the token's validity (checking for expiration or
    tampering). If the token is invalid or expired, it flashes an error message
    and redirects to the login page.

    Args:
        token (str, optional): The token used to verify the password reset
        request.

    Returns:
        Response: Depending on the request type and token validity:
        - Renders the password reset form on GET if the token is valid.
        - Redirects to the login page on invalid/expired token or post-reset.
        - Flashes an appropriate message based on the action outcome
        (error/success).
    """
    if token:
        try:
            email = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])\
                .loads(token, salt='reset-password-salt', max_age=3600)
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
                logout_user()
                flash('Your password has been reset.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Password cannot be empty.', 'error')

        return render_template('reset_password.html', token=token)
    else:
        flash("Token Not Specified")
        return redirect(url_for("core.home"))


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handles the password reset request process for users.

    This endpoint functions differently based on the request method:
      - GET: It renders a form for users to enter their email address to
      initiate the password reset process.
      - POST: It collects the email address submitted through the form. If an
      email address is provided, it redirects the user to the route that sends
      a password reset confirmation email.

    Returns:
        Response:
            - Renders the 'forgot_password.html' template on GET requests.
            - Redirects to the 'send_confirmation' route with the user's email
            on successful POST requests.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        return redirect(url_for('auth.send_confirmation', email=email))

    return render_template('forgot_password.html')


@auth_bp.route('/reg_confirmation', methods=['GET', 'POST'])
def reg_confirmation():
    """
    Handles the email confirmation process for new user registrations.

    This function operates differently based on the HTTP request method:
      - GET: Renders a form for users to submit their email address to receive
      a registration confirmation link.
      - POST: Takes the provided email from the form, checks if it's already
      registered, generates a secure token using the application's secret key,
      constructs a URL for registration confirmation with the token, and sends
      an email to the user with this link. Upon successfully sending the email,
      it flashes a success message and redirects the user back to the
      confirmation page.

    Returns:
        Response:
            - On GET requests: Renders the 'reg_email.html' template where
            users can enter their email.
            - On POST requests: Redirects back to the 'reg_confirmation' page
            with a success message if the email is not currently in use,
            otherwise displays an error message.
    """
    if request.method == 'POST':
        email = request.form.get("reg_email")
        existing_email_check = User.find_by_email(email)
        if existing_email_check:
            flash("That email address is already in use.")
            return redirect(url_for('auth.reg_confirmation'))
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='reg-confirmation-salt')
        confirmation_url = url_for(
            'auth.register', token=token, _external=True
            )
        msg = Message("Confirm email address to register", recipients=[email])
        msg.body = (
            f"To confirm email, please visit the following link: "
            f"{confirmation_url}"
            )
        mail.send(msg)
        flash('A confirmation email has been sent.', 'success')
        return redirect(url_for('auth.reg_confirmation'))

    return render_template('reg_email.html')


@auth_bp.route("/register", defaults={"token": None})
@auth_bp.route("/register/<token>", methods=["GET", "POST"])
def register(token):
    """
    Handles the user registration process through a token-verified email
    confirmation link.

    This function checks the validity of a provided token to confirm the user's
    email address. If the token is valid, it:
      - Renders a registration form on GET requests.
      - Registers the user using the provided details from the form on POST
      requests.
    If the token is invalid or expired, it redirects to the email confirmation
    page with an error message.
    Additional checks ensure:
      - Users with an existing username are notified via an error message.
      - Already authenticated users are redirected to the home page.

    Args:
        token (str, optional): The token used to verify the email confirmation
        request.

    Returns:
        Response:
            - Renders the 'register.html' template on valid GET requests.
            - Redirects to the 'reg_confirmation' page with an error on token
            issues.
            - Redirects to the 'login' page on username conflict.
            - Redirects to the 'profile' page on successful registration.
            - Redirects to the 'home' page if the user is already
            authenticated.

    Raises:
        SignatureExpired: If the token has expired, indicating a timeout for
        the registration link.
        BadSignature: If the token is invalid, indicating a potentially
        tampered or incorrect link.
    """
    if token:
        try:
            email = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])\
                .loads(token, salt='reg-confirmation-salt', max_age=3600)
        except SignatureExpired:
            flash('The registration link has expired.', 'error')
            return redirect(url_for('auth.reg_confirmation'))
        except BadSignature:
            flash('The registration link is invalid.', 'error')
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
    else:
        flash("Token Not Specified")
        return redirect(url_for("core.home"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Manages the user login process via a web form.

    This function supports both GET and POST requests for handling user
    authentication:
      - GET: Renders the login form.
      - POST: Accepts and processes the login form data. It verifies the
      username and password, logs the user in if the credentials are verified,
      and then redirects them to their profile page. If the user is already
      authenticated, they are redirected to the questions page immediately.

    Returns:
        Response:
            - Renders the 'login.html' template on GET requests.
            - Redirects to the Posts page if the user is already authenticated.
            - Redirects to the Profile page with a welcome message upon
            successful login.
            - Redirects back to the Log In page with an error message if the
            credentials are incorrect.
    """
    if current_user.is_authenticated:
        return redirect(url_for('posts.get_posts'))

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

    This function logs out the currently authenticated user, flashes a logout
    success message, and redirects the user to the login page.

    Returns:
        Response: A redirect response to the login page after logging out the
        user.
    """
    logout_user()
    flash("Logged Out")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", defaults={"username": None})
@auth_bp.route("/profile/<username>")
@login_required
def profile(username):
    """
    Displays the profile page for a specified or currently authenticated user.

    If a username is provided, the function retrieves and displays the profile
    of that user along with posts that they have made. If no username is
    provided, or if the specified username does not match any existing user,
    the function defaults to the profile of the currently authenticated user.
    In the case of an incorrect or missing username, a flash message is
    displayed and the user is redirected to their own profile.

    Args:
        username (str, optional): The username of the user whose profile is to
        be displayed. If not provided, the profile of the current user is used.

    Returns:
        Response:
            - Renders the 'profile.html' template with the user's information
            and their associated posts, if the username is valid.
            - Redirects to the profile page of the current user with an
            appropriate message if the username is incorrect or not specified.
    """
    if username:
        posts = Post.get_list_by_username(username)
        user = User.find_by_username(username, True)
        if user is None:
            flash("User Not Found")
            return redirect(
                url_for("auth.profile", username=current_user.username)
                )

        return render_template("profile.html", user=user, posts=posts)
    else:
        flash("Username Not Specified")
        return redirect(
            url_for("auth.profile", username=current_user.username)
            )


def user_owns_profile_or_admin(f):
    """
    Decorator to verify if the current user is the owner of the profile or an
    admin.

    This decorator checks if the current user's username matches the username
    specified in the route parameter or if the current user has an "Admin"
    role. If neither condition is met, the decorator flashes an error message
    about unauthorized access and redirects the user to their own profile page.

    This is useful for protecting views that should only be accessible by the
    user themselves or administrators.

    Args:
        f (function): The view function that this decorator is applied to.

    Returns:
        function: The wrapped view function which includes the authorization
        check.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        username = kwargs.get('username')
        if current_user.username != username and current_user.role != "Admin":
            flash("You are not authorized to do this.", "error")
            return redirect(
                url_for('auth.profile', username=current_user.username)
                )
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route("/edit_profile", defaults={"username": None})
@auth_bp.route("/edit_profile/<username>", methods=["GET", "POST"])
@login_required
@user_owns_profile_or_admin
def edit_profile(username):
    """
    Handles the editing of a user's profile.

    On a GET request, renders the edit_profile template, pre-filled with
    existing user data.
    On a POST request, it updates the user's profile with the provided data.

    The function prevents the submission of an email address that is already in
    use.

    Args:
        username (str): The username of the user whose profile is to be edited.

    Returns:
        Response: Renders the edit_profile template on GET requests.
        Response: Redirects to user's profile page if the email address is
        already in use.
        Response: Redirects to the user's profile page after successful profile
        update.
        Response: Redirects to the Users page if the current user is an Admin.
        Response: Redirects to the current user's profile page if they are not
        authorized to edit the profile.
    """
    if username:
        if request.method == "POST":
            email = request.form.get("email")
            found_user = User.find_by_email(email)
            if found_user:
                if found_user.username != username:
                    flash("That email is already in use")
                    return redirect(
                        url_for('auth.profile', username=current_user.username)
                        )
            role = request.form.get("role")
            level = request.form.get("level")
            provider = request.form.get("provider")
            location = request.form.get("location")
            bio = request.form.get("bio")
            User.update_profile(
                email, username, role, level, provider, location, bio
                )
            flash("Profile Updated", "success")
            if current_user.role == "Admin":
                return redirect(url_for('auth.view_users'))
            else:
                return redirect(url_for('auth.profile', username=username))

        user = User.find_by_username(username, True)
        if user is None:
            flash("User Not Found")
            return redirect(
                url_for("auth.profile", username=current_user.username)
                )
        roles = Core.get_roles()
        levels = Core.get_levels()
        providers = Core.get_providers()

        return render_template(
            "edit_profile.html",
            user=user,
            roles=roles,
            levels=levels,
            providers=providers
            )

    else:
        flash("Username Not Specified")
        return redirect(
            url_for("auth.profile", username=current_user.username)
            )


@auth_bp.route("/delete_profile", defaults={"username": None})
@auth_bp.route("/delete_profile/<username>")
@login_required
@user_owns_profile_or_admin
def delete_profile(username):
    """
    Deletes a user's profile.

    Verifies if the current user is authorized to delete the profile (either
    the profile owner or an Admin). If authorized, it deletes the user's
    profile, flashes a success message, and redirects accordingly.

    Args:
        username (str): The username of the user whose profile is to be
        deleted.

    Returns:
        Response: Redirects to the current user's profile page if they are not
        authorized to delete the profile.
        Response: Redirects to the users view page if the current user is an
        Admin.
        Response: Redirects to the login page after successful profile deletion
        if the current user is not an Admin.
    """
    if username:
        user_search = User.find_by_username(username, True)
        if user_search is None:
            flash("User Not Found")
            return redirect(
                url_for("auth.profile", username=current_user.username)
                )
        User.delete_profile(username)
        flash("Account Deleted")
        if current_user.role == "Admin":
            return redirect(url_for("auth.view_users"))
        else:
            logout_user()
            return redirect(url_for("auth.login"))
    else:
        flash("Username Not Specified")
        return redirect(
            url_for("auth.profile", username=current_user.username)
            )


@auth_bp.route("/view_users", methods=["GET", "POST"])
@login_required
def view_users():
    """
    Displays and filters the list of users.

    On a GET request, it retrieves all users and renders the users view
    template.
    On a POST request, it filters the users based on the provided form data
    (level, provider, username, email, location) and then renders the users
    view template with the filtered results.

    Returns:
        Response: Renders the users view template with the list of users and
        additional context data.
    """
    if current_user.role == 'Student':
        flash("Unauthorized")
        return redirect(
            url_for("auth.profile", username=current_user.username)
            )

    users, query = User.get_users(None, None, None, None, None)

    if request.method == 'POST':
        level = request.form.get('level')
        provider = request.form.get('provider')
        username = request.form.get('username')
        email = request.form.get('email')
        location = request.form.get('location')
        users, query = User.get_users(
            level, provider, username, email, location
            )

    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    levels = Core.get_levels()
    providers = Core.get_providers()

    return render_template(
        "users.html",
        users=users,
        query=query,
        groups=groups,
        levels=levels,
        providers=providers)
