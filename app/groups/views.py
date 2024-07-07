from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.groups.models import Group


groups_bp = Blueprint('groups', __name__, template_folder='../templates')


@groups_bp.route("/get_groups")
@login_required
def get_groups():
    """
    Renders the groups template, featuring a list of groups, filtered by role and username.
    """
    groups = Group.get_groups_by_role(current_user.role, current_user.username)

    return render_template("groups.html", groups=groups)


@groups_bp.route("/add_group", methods=["GET", "POST"])
@login_required
def add_group():
    """
    Renders the add_group template.

    If POST:
    Inserts a group into the database.

    Flashes message to user.
    """
    if request.method == "POST":
        tutor = current_user.username
        provider = request.form.get("provider")
        level = request.form.get("level")
        year = request.form.get("year")
        weekday = request.form.get("weekday")
        Group.insert_group(tutor, provider, level, year, weekday)
        flash("Group created")

    providers = Group.get_providers()
    levels = Group.get_levels()

    return render_template("add_group.html", providers=providers, levels=levels)


@groups_bp.route("/add_student/<username>", methods=["GET", "POST"]) # just post?
@login_required
def add_student(username):
    """
    Adds a student to a group's students list property.

    Flashes message to user.

    Redirects to get_groups view.
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
    Removes a student from a group's students list property.

    Flashes message to user.

    Redirects to get_groups view.
    """
    Group.remove_student(group_id, username)
    flash("Student removed")

    return redirect(url_for('groups.get_groups'))