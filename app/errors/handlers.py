from flask import Blueprint, render_template


errors_bp = Blueprint('errors', __name__, template_folder='../templates')


@errors_bp.app_errorhandler(404)
def error_404(error):
    """
    Handles 404 Not Found errors.

    This function is triggered when a 404 error occurs, which means the requested resource could not be found.
    It renders and returns the custom 404 error page template.

    Args:
        error (Exception): The exception object representing the 404 error.

    Returns:
        tuple: A tuple containing the rendered 404 error page template and the 404 status code.
    """

    return render_template('404.html'), 404


@errors_bp.app_errorhandler(500)
def error_500(error):
    """
    Handles 500 Internal Server Error errors.

    This function is triggered when a 500 error occurs, which means the server encountered an unexpected condition
    that prevented it from fulfilling the request. It renders and returns the custom 500 error page template.

    Args:
        error (Exception): The exception object representing the 500 error.

    Returns:
        tuple: A tuple containing the rendered 500 error page template and the 500 status code.
    """
    
    return render_template('500.html'), 500
