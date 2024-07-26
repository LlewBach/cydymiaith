from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app.answers.models import Answer
from app.questions.models import Question


answers_bp = Blueprint('answers', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@answers_bp.route("/view_comments/<question_id>")
def view_comments(question_id):
    """
    Renders the view_answers template for a specific question.

    This function retrieves the question and its associated answers from the database,
    sets the time ago for the question, counts the number of answers, and then renders
    the view_answers template with this data.

    Args:
        question_id (str): The ID of the question for which answers are to be viewed.

    Returns:
        Response: Renders the view_answers.html template with the question, answers, and the count of answers.
    """
    question = Question.find_by_id(question_id)
    Question.set_time_ago(question)
    answers = Answer.find_answers_by_question_id(question_id)
    answer_count = Answer.count_answers(answers)

    return render_template("view_answers.html", question=question, answers=answers, answer_count=answer_count)


@answers_bp.route("/answer", defaults={"question_id": None})
@answers_bp.route("/answer/<question_id>", methods=["GET", "POST"])
@login_required
def answer(question_id):
    """
    Adds an answer to a specific question and updates the database.

    On a POST request, it retrieves the answer text from the form, inserts the answer into the database, increases the answer count for the question, flashes a success message to the user, and redirects to the view_answers template to display the updated list of answers.

    Args:
        question_id (str): The ID of the question to which the answer is to be added.

    Returns:
        Response: Redirects to the view_answers template to display the updated list of answers.
    """
    if question_id:
        if request.method == "POST":
            text = request.form.get("text")
            username = current_user.username
            Answer.insert_answer(question_id, text, username)
            Question.increase_answer_count(question_id)
            flash("Comment added")

            return redirect(url_for("answers.view_comments", question_id=question_id))
    else:
        flash("Post Not Specified")
        return redirect(url_for("questions.get_posts"))
    

def user_owns_answer_or_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        answer_id = kwargs.get('answer_id')
        answer = Answer.find_by_id(answer_id)
        if answer is None:
            flash("Comment Not Specified", "error")
            return redirect(url_for('questions.get_posts'))
        if current_user.username != answer['username'] and current_user.role != 'Admin':
            flash("You are not authorized to do this.", "error")
            return redirect(url_for('auth.profile', username=current_user.username))
        return f(*args, **kwargs)
    return wrapper


@answers_bp.route("/edit_comment", defaults={"answer_id": None})
@answers_bp.route("/edit_comment/<answer_id>", methods=["GET", "POST"])
@login_required
@user_owns_answer_or_admin
def edit_comment(answer_id):
    """
    Handles the editing of an existing answer and updates the database.

    On a GET request, it renders the edit_answer template with the current answer details. On a POST request, it updates the answer in the database with the provided text, flashes a success message to the user, and redirects
    to the view_answers template to display the updated list of answers.

    Args:
        answer_id (str): The ID of the answer to be edited.

    Returns:
        Response: Renders the edit_answer.html template with the current answer details on a GET request.
        Response: Redirects to the view_answers template to display the updated list of answers on a POST request.
    """
    question_id = Answer.find_question_id(answer_id)

    if request.method == "POST":
        text = request.form.get("text")
        username = current_user.username
        Answer.edit_answer(answer_id, question_id, text, username)
        flash("Comment Edited")

        return redirect(url_for("answers.view_comments", question_id=question_id))
    
    question = Question.find_by_id(question_id)
    answers = Answer.find_answers_by_question_id(question_id)

    return render_template("edit_answer.html", question=question, answers=answers, answer_id=ObjectId(answer_id))


@answers_bp.route("/delete_answer", defaults={"answer_id": None})
@answers_bp.route("/delete_answer/<answer_id>")
@login_required
@user_owns_answer_or_admin
def delete_answer(answer_id):
    """
    Deletes a specific answer from the database and updates the associated question's answer count.

    This function deletes an answer from the database, decreases the answer count of the associated question, flashes a success message to the user, and redirects to the view_answers template to display the updated list
    of answers.

    Args:
        answer_id (str): The ID of the answer to be deleted.

    Returns:
        Response: Redirects to the view_answers template to display the updated list of answers.
    """
    question_id = Answer.find_question_id(answer_id)
    Question.decrease_answer_count(question_id)
    Answer.delete_answer(answer_id)
    flash("Comment Deleted")
    
    return redirect(url_for("answers.view_comments", question_id=question_id))