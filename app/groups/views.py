from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.groups.models import Group


groups_bp = Blueprint('groups', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@groups_bp.route("/get_groups")
@login_required
def get_groups():
    """
    Renders the groups template with a list of groups filtered by the current user's role and username.

    This function retrieves the list of groups from the database based on the current user's role and username. It then renders the groups template, passing the filtered list of groups to the template.

    Returns:
        Response: Renders the groups.html template with the list of groups filtered by the user's role and username.
    """
    groups = Group.get_groups_by_role(current_user.role, current_user.username)

    return render_template("groups.html", groups=groups)


@groups_bp.route("/add_group", methods=["GET", "POST"])
@login_required
def add_group():
    """
    Handles the creation of a new group and renders the add_group template.

    On a GET request, this function renders the add_group template with the necessary 
    data for creating a group. On a POST request, it inserts a new group into the database
    using the provided form data, flashes a success message to the user, and redirects to the get_groups view.

    Returns:
        Response: 
            - On GET: Renders the add_group.html template with the list of providers and levels.
            - On POST: Redirects to the get_groups view after successfully creating a group.
    """
    if request.method == "POST":
        tutor = current_user.username
        provider = request.form.get("provider")
        level = request.form.get("level")
        year = request.form.get("year")
        weekday = request.form.get("weekday")
        Group.insert_group(tutor, provider, level, year, weekday)
        flash("Group created")
        return redirect(url_for('groups.get_groups'))

    providers = Group.get_providers()
    levels = Group.get_levels()

    return render_template("add_group.html", providers=providers, levels=levels)


@groups_bp.route("/add_student/<username>", methods=["GET", "POST"]) # just post?
@login_required
def add_student(username):
    """
    Adds a student to a group's students list and redirects to the groups view.

    On a POST request, this function retrieves the group ID from the form data and adds the specified student (by username) to the group's students list in the database. It then flashes a success message to the user and redirects to the get_groups view.

    Args:
        username (str): The username of the student to be added to the group.

    Returns:
        Response: Redirects to the get_groups view.
    """
    if request.method == "POST":
        group_id = request.form.get("group_id")
        Group.add_student_to_group(group_id, username)
        flash("Student added")

    return redirect(url_for("groups.get_groups"))


@groups_bp.route("/remove_student/<group_id>/<username>")
@login_required
def remove_student(group_id, username):
    """
    Removes a student from a group's students list and redirects to the groups view.

    This function removes the specified student (by username) from the group's students list
    in the database. It then flashes a success message to the user and redirects to the get_groups view.

    Args:
        group_id (str): The ID of the group from which the student is to be removed.
        username (str): The username of the student to be removed from the group.

    Returns:
        Response: Redirects to the get_groups view.
    """
    Group.remove_student(group_id, username)
    flash("Student removed")

    return redirect(url_for('groups.get_groups'))


@groups_bp.route("/delete_group/<group_id>")
@login_required
def delete_group(group_id):
    """
    Deletes a group and redirects to the groups list view.

    This route handles the deletion of a group specified by the group_id.
    It calls the Group.delete_group method to perform the deletion, flashes
    a success message to the user, and redirects to the 'get_groups' view.

    Args:
        group_id (str): The unique identifier of the group to be deleted.

    Returns:
        Response: A redirect response to the 'get_groups' view.
    """
    Group.delete_group(group_id)
    flash("Group deleted")

    return redirect(url_for('groups.get_groups'))