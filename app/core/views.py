from flask import Blueprint, render_template

core_bp = Blueprint('core', __name__, template_folder='../templates')


@core_bp.route("/")
@core_bp.route("/home")
def home():
    """
    Renders the home page template.

    Returns:
        Response: The rendered "home.html" template.
    """
    return render_template("home.html")