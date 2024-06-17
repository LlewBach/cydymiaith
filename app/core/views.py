from flask import Blueprint, render_template

core_bp = Blueprint('core', __name__, template_folder='../templates')


@core_bp.route("/")
@core_bp.route("/home")
def home():
    return render_template("home.html")