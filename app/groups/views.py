from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.groups.models import Group
from app.auth.models import User


groups_bp = Blueprint('groups', __name__, template_folder='../templates')


@groups_bp.route("/get_groups")
def get_groups():
    groups = Group.get_all_groups()

    return render_template("groups.html", groups=groups)


@groups_bp.route("/add_group", methods=["GET", "POST"])
def add_group():
    if request.method == "POST":
        tutor = current_user.username
        provider = request.form.get("provider")
        level = request.form.get("level")
        year = request.form.get("year")
        weekday = request.form.get("weekday")
        Group.insert_group(tutor, provider, level, year, weekday)

    providers = Group.get_providers()
    levels = Group.get_levels()

    return render_template("add_group.html", providers=providers, levels=levels)


@groups_bp.route("/add_student/<username>", methods=["GET", "POST"]) # just post?
def add_student(username):
    if request.method == "POST":
        group_id = request.form.get("group_id")
        # student = Group.get_student_by_username(username)
        Group.add_student_to_group(group_id, username)

    return redirect(url_for("groups.get_groups"))


@groups_bp.route("/remove_student/<group_id>/<username>")
def remove_student(group_id, username):
    Group.remove_student(group_id, username)

    return redirect(url_for('groups.get_groups'))