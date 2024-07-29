from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.core.models import Core
from app.groups.models import Group
from app.auth.models import User


groups_bp = Blueprint('groups', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
def must_be_tutor_or_admin(f):
    """
    Decorator to ensure that the current user has either 'Tutor' or 'Admin'
    role.

    This decorator is used to restrict access to certain view functions only to
    users with specific roles. If the current user does not have the 'Tutor' or
    'Admin' role, it flashes an unauthorized access message and redirects the
    user to their profile page. This is useful for protecting endpoints that
    should be accessible only by users in these roles.

    Args:
        f (function): The view function to wrap.

    Returns:
        function: The wrapped function with added role-based access control.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role not in ["Admin", "Tutor"]:
            flash("You are not authorized to do this.", "error")
            return redirect(
                url_for('auth.profile', username=current_user.username)
                )
        return f(*args, **kwargs)
    return wrapper


@groups_bp.route("/get_groups")
@login_required
@must_be_tutor_or_admin
def get_groups():
    """
    Renders the groups template with a list of groups filtered by the current
    user's role and username.

    This function retrieves the list of groups from the database based on the
    current user's role and username. It then renders the groups template,
    passing the filtered list of groups to the template.

    Returns:
        Response: Renders the groups.html template with the list of groups
        filtered by the user's role and username.
    """
    groups = Group.get_groups_by_role(current_user.role, current_user.username)

    return render_template("groups.html", groups=groups)


@groups_bp.route("/add_group", methods=["GET", "POST"])
@login_required
@must_be_tutor_or_admin
def add_group():
    """
    Handles the creation of a new group and renders the add_group template.

    On a GET request, this function renders the add_group template with the
    necessary data for creating a group.
    On a POST request, it inserts a new group into the database using the
    provided form data, flashes a success message to the user, and redirects to
    the get_groups view.

    Returns:
        Response:
            - On GET: Renders the add_group.html template with the list of
            providers and levels.
            - On POST: Redirects to the get_groups view after successfully
            creating a group.
    """
    if request.method == "POST":
        tutor = current_user.username
        provider = request.form.get("provider")
        level = request.form.get("level")
        year = request.form.get("year")
        weekday = request.form.get("weekday")
        Group.insert_group(tutor, provider, level, year, weekday)
        flash("Group Created")
        return redirect(url_for('groups.get_groups'))

    providers = Core.get_providers()
    levels = Core.get_levels()

    return render_template(
        "add_group.html",
        providers=providers,
        levels=levels
        )


@groups_bp.route("/add_student", defaults={"username": None}, methods=['POST'])
@groups_bp.route("/add_student/<username>", methods=['POST'])
@login_required
@must_be_tutor_or_admin
def add_student(username):
    """
    Adds a student to a specific group based on form submissions and redirects
    to the group management view.

    This function is accessible via POST request where it processes the
    inclusion of a specified student into a designated group. If a username is
    provided, the function attempts to find the user and, subsequently, the
    group ID from the form data. If both the user and the group are validated,
    the student is added to the group's students list in the database. The
    function handles different scenarios such as missing user, missing group
    ID, or unspecified student by flashing appropriate messages and redirecting
    accordingly.

    Args:
        username (str, optional): The username of the student to be added to
        the group.

    Returns:
        Response: Redirects to the groups management view, flashing success or
        error messages based on the outcome of the operation.
    """
    if username:
        user_search = User.find_by_username(username, True)
        if user_search is None:
            flash("User Not Found")
            return redirect(url_for("auth.view_users"))
        group_id = request.form.get("group_id")
        if group_id:
            Group.add_student_to_group(group_id, username)
            flash("Student Added")
        else:
            flash("Group ID not provided", "error")

        return redirect(url_for("groups.get_groups"))
    else:
        flash("Student Not Specified")
        return redirect(url_for("auth.view_users"))


@groups_bp.route("/remove_student", defaults={
    "group_id": None, "username": None
    })
@groups_bp.route("/remove_student/<group_id>", defaults={"username": None})
@groups_bp.route("/remove_student/<group_id>/<username>")
@login_required
@must_be_tutor_or_admin
def remove_student(group_id, username):
    """
    Removes a student from a specific group based on the provided group ID and
    student username.

    This function is responsible for removing a specified student from a
    designated group's student list. It validates the presence of both a group
    ID and a student username. If both are provided, it proceeds to remove the
    student from the group. A success message is flashed to the user upon
    successful removal. If either the group ID or username is missing, it
    flashes an error message indicating that both pieces of information are
    necessary.

    Args:
        group_id (str, optional): The ID of the group from which the student is
        to be removed. Required for the operation to proceed.
        username (str, optional): The username of the student to be removed
        from the group. Required for the operation to proceed.

    Returns:
        Response: Redirects to the groups management view, flashing messages
        based on the success or failure of the student removal operation.
    """
    if group_id and username:
        Group.remove_student(group_id, username)
        flash("Student Removed")
        return redirect(url_for('groups.get_groups'))
    else:
        flash("Group and Student Not Specified")
        return redirect(url_for("groups.get_groups"))


@groups_bp.route("/edit_group", defaults={"group_id": None})
@groups_bp.route("/edit_group/<group_id>", methods=["GET", "POST"])
@login_required
@must_be_tutor_or_admin
def edit_group(group_id):
    """
    Manages the editing of an existing group's details.

    This function handles both GET and POST requests for a specific group based
    on the group ID provided.
    - On a GET request, it retrieves the group's details and displays them in a
    form for editing.
    - On a POST request, it updates the group with the data provided in the
    form and then redirects to the group management view.

    If no group ID is provided, or if the specified group cannot be found, it
    flashes an appropriate error message and redirects to the group listing
    page.

    Args:
        group_id (str, optional): The ID of the group to be edited. If not
        provided, the function will return to the group listing.

    Returns:
        Response:
            - On GET requests: Renders the 'edit_group.html' template with the
            current group details, providers, and levels available for
            selection.
            - On POST requests: Saves the changes and redirects to the group
            management view with a success message.
            - On missing or not found group_id: Redirects to the group
            management view with an error message.
    """
    if group_id:
        group = Group.get_group_by_id(group_id)
        if group is None:
            flash("No Group Found")
            return redirect(url_for("groups.get_groups"))
        if request.method == "POST":
            tutor = current_user.username
            provider = request.form.get("provider")
            level = request.form.get("level")
            year = request.form.get("year")
            weekday = request.form.get("weekday")
            students = group["students"]
            Group.edit_group(
                group_id, tutor, provider, level, year, weekday, students
                )
            flash("Group Edited")
            return redirect(url_for('groups.get_groups'))

        providers = Core.get_providers()
        levels = Core.get_levels()

        return render_template(
            "edit_group.html",
            group=group,
            providers=providers,
            levels=levels)

    else:
        flash("Group Not Specified")
        return redirect(url_for("groups.get_groups"))


@groups_bp.route("/delete_group", defaults={"group_id": None})
@groups_bp.route("/delete_group/<group_id>")
@login_required
@must_be_tutor_or_admin
def delete_group(group_id):
    """
    Deletes a specific group from the database and redirects to the group
    management view.

    This function checks if a valid group ID is provided and verifies if the
    group exists. If the group exists, it proceeds with deletion using the
    Group.delete_group method. Upon successful deletion, a success message is
    flashed. If no group is found or if no group ID is provided, it flashes an
    error message accordingly.

    Args:
        group_id (str, optional): The unique identifier of the group to be
        deleted. If not provided, the function will flash an error and
        redirect.

    Returns:
        Response: Redirects to the 'get_groups' view after attempting to delete
        a group. The redirect is accompanied by either a success message (if
        deletion is successful) or an error message (if the group is not found
        or the group ID is not specified).
    """
    if group_id:
        group = Group.get_group_by_id(group_id)
        if group is None:
            flash("No Group Found")
            return redirect(url_for("groups.get_groups"))
        Group.delete_group(group_id)
        flash("Group Deleted")
    else:
        flash("Group Not Specified")

    return redirect(url_for("groups.get_groups"))
