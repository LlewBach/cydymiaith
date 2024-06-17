from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app.answers.models import Answer
from app.questions.models import Question


answers_bp = Blueprint('answers', __name__, template_folder='../templates')

@answers_bp.route("/view_answers/<question_id>")
def view_answers(question_id):
    question = Question.find_by_id(question_id)
    Question.set_time_ago(question)
    answers = Answer.find_answers_by_question_id(question_id)
    # answer_count = len(answers)
    answer_count = Answer.count_answers(answers)

    return render_template("view_answers.html", question=question, answers=answers, answer_count=answer_count)


@answers_bp.route("/answer/<question_id>", methods=["GET", "POST"])
@login_required
def answer(question_id):
    if request.method == "POST":
        text = request.form.get("text")
        # username = session["user"]
        username = current_user.username
        Answer.insert_answer(question_id, text, username)
        Question.increase_answer_count(question_id)
        return redirect(url_for("answers.view_answers", question_id=question_id))
    

@answers_bp.route("/edit_answer/<answer_id>", methods=["GET", "POST"])
@login_required
def edit_answer(answer_id):
    question_id = Answer.find_question_id(answer_id)

    if request.method == "POST":
        text = request.form.get("text")
        username = current_user.username
        Answer.edit_answer(answer_id, question_id, text, username)
        return redirect(url_for("answers.view_answers", question_id=question_id))
    
    question = Question.find_by_id(question_id)
    answers = Answer.find_answers_by_question_id(question_id)
    return render_template("edit_answer.html", question=question, answers=answers, answer_id=ObjectId(answer_id))


@answers_bp.route("/delete_answer/<answer_id>")
@login_required
def delete_answer(answer_id):
    question_id = Answer.find_question_id(answer_id)
    Question.decrease_answer_count(question_id)
    Answer.delete_answer(answer_id)
    flash("Answer deleted")
    return redirect(url_for("answers.view_answers", question_id=question_id))