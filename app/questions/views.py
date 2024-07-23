from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.questions.models import Question
from app.groups.models import Group


questions_bp = Blueprint('questions', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@questions_bp.route("/get_posts", methods=["GET", "POST"])
def get_posts():
    """
    Renders the questions template showing a list of all questions or filtered questions.

    On a GET request, this function retrieves all questions and renders the questions template.
    It also retrieves the categories and groups relevant to the current user's role and username.

    On a POST request, it retrieves the category and group ID from the form data, filters the questions
    based on these parameters, and then renders the questions template with the filtered list of questions.

    Returns:
        Response: Renders the questions.html template with the list of questions, categories, and groups.
    """
    categories = Question.get_categories()
    questions, query = Question.get_list(None, None)
    groups = Group.get_groups_by_role(current_user.role, current_user.username) if current_user.is_authenticated else []

    if request.method == "POST":
        category = request.form.get("category")
        group_id = request.form.get("group")
        questions, query = Question.get_list(category, group_id)

    return render_template("questions.html", questions=questions, categories=categories, groups=groups, query=query)


@questions_bp.route("/ask_question", methods=["GET", "POST"])
@login_required
def ask_question():
    """
    Handles the creation of a new question and renders the ask_question template.

    On a GET request, this function renders the ask_question template with the necessary
    data for creating a question, including the list of categories and groups relevant to
    the current user's role and username.

    On a POST request, it retrieves the form data, inserts the new question into the database,
    flashes a success message to the user, and redirects to the get_posts view.

    Returns:
        Response: Renders the ask_question.html template with the list of categories and groups on a GET request.
        Response: Redirects to the get_posts view on a POST request.
    """
    if request.method == "POST":
        username = current_user.username
        category = request.form.get("category")
        group_id = request.form.get("group")
        title = request.form.get("title")
        description = request.form.get("description")
        Question.insert_question(username, category, group_id, title, description)
        flash("Post Published")
        return redirect(url_for('questions.get_posts'))

    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    categories = Question.get_categories()
    return render_template("ask_question.html", categories=categories, groups=groups)


def user_owns_question_or_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        question_id = kwargs.get('question_id')
        question = Question.find_by_id(question_id)
        if question is None:
            flash("Question not found.", "error")
            return redirect(url_for('questions.get_posts'))
        if current_user.username != question['username'] and current_user.role != 'Admin':
            flash("You are not authorized to do this.", "error")
            return redirect(url_for('auth.profile', username=current_user.username))
        return f(*args, **kwargs)
    return wrapper


@questions_bp.route("/edit_question/<question_id>", methods=["GET", "POST"])
@login_required
@user_owns_question_or_admin
def edit_question(question_id):
    """
    Handles the editing of an existing question and renders the edit_question template.

    On a GET request, this function retrieves the question by its ID and renders the edit_question template with the question's current data.

    On a POST request, it retrieves the updated title and description from the form data, updates the question in the database, flashes a success message to the user, and redirects to the get_posts view.

    Args:
        question_id (str): The ID of the question to be edited.

    Returns:
        Response: Renders the edit_question.html template with the question's current data on a GET request.
        Response: Redirects to the get_posts view on a POST request.
    """
    if request.method == "POST":
        username = current_user.username
        category = request.form.get("category")
        group_id = request.form.get("group")
        title = request.form.get("title")
        description = request.form.get("description")
        Question.update_question(question_id, username, category, group_id, title, description)
        flash("Post Updated")
        return redirect(url_for('questions.get_posts'))
    
    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    categories = Question.get_categories()
    question = Question.find_by_id(question_id)
    return render_template("edit_question.html", question=question, groups=groups, categories=categories)


@questions_bp.route("/delete_question/<question_id>")
@login_required
@user_owns_question_or_admin
def delete_question(question_id):
    """
    Deletes a question from the database and redirects to the get_posts view.

    This function deletes the specified question from the database. It then flashes a success message
    to the user and redirects to the get_posts view.

    Args:
        question_id (str): The ID of the question to be deleted.

    Returns:
        Response: Redirects to the get_posts view after deleting the question.
    """
    Question.delete_question(question_id)
    flash("Post Deleted")
    return redirect(url_for("questions.get_posts"))