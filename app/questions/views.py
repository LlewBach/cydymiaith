from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.questions.models import Question
from app.groups.models import Group

questions_bp = Blueprint('questions', __name__, template_folder='../templates')


@questions_bp.route("/get_questions", methods=["GET", "POST"])
def get_questions():
    categories = Question.get_categories()
    questions = Question.get_list(None, None)
    # if current_user.role == 'Tutor':
    #     groups = Group.get_own_groups(current_user.username)
    # elif current_user.role == 'Student':
    #     groups = Group.get_student_group(current_user.username)
    # elif current_user.role == 'Admin':
    #     groups = Group.get_all_groups()
    groups = Group.get_groups_by_role(current_user.role, current_user.username)

    if request.method == "POST":
        category = request.form.get("category")
        group_id = request.form.get("group")
        questions = Question.get_list(category, group_id)

    return render_template("questions.html", questions=questions, categories=categories, groups=groups)


@questions_bp.route("/ask_question", methods=["GET", "POST"])
@login_required
def ask_question():
    if request.method == "POST":
        # username = session["user"]
        username = current_user.username
        category = request.form.get("category")
        group_id = request.form.get("group")
        title = request.form.get("title")
        description = request.form.get("description")
        Question.insert_question(username, category, group_id, title, description)
        flash("Question posted to community:)")
        return redirect(url_for('questions.get_questions'))

    groups = Group.get_own_groups(current_user.username)
    categories = Question.get_categories()
    return render_template("ask_question.html", categories=categories, groups=groups)


@questions_bp.route("/edit_question/<question_id>", methods=["GET", "POST"])
@login_required
def edit_question(question_id):
    if request.method == "POST":
        # username = session["user"]
        username = current_user.username
        title = request.form.get("title")
        description = request.form.get("description")
        Question.update_question(question_id, username, title, description)
        flash("Question updated")
        return redirect(url_for('questions.get_questions'))
    
    question = Question.find_by_id(question_id)
    return render_template("edit_question.html", question=question)


@questions_bp.route("/delete_question/<question_id>")
@login_required
def delete_question(question_id):
    Question.delete_question(question_id)
    # Need to also delete all associated answers
    flash("Question deleted")
    return redirect(url_for("questions.get_questions"))