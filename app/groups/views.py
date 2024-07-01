from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.groups.models import Group



groups_bp = Blueprint('groups', __name__, template_folder='../templates')


@groups_bp.route("/get_groups")
def get_groups():
    groups = Group.get_all_groups()

    return render_template("groups.html", groups=groups)


@groups_bp.route("/add_group")
def add_group():
    pass