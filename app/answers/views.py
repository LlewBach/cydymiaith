from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import humanize
import pytz
from bson.objectid import ObjectId
from app import mongo
from app.answers.models import Answer


answers_bp = Blueprint('answers', __name__, template_folder='../templates/answers')

@answers_bp.route("/view_answers/<question_id>")
def view_answers(question_id):
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    creation_time = question['_id'].generation_time.replace(tzinfo=pytz.utc)
    question['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
    # answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
    answers = Answer.find_answers_by_question_id(question_id)
    # answer_count = len(answers)
    answer_count = Answer.count_answers(answers)

    return render_template("view_answers.html", question=question, answers=answers, answer_count=answer_count)


@answers_bp.route("/answer/<question_id>", methods=["GET", "POST"])
def answer(question_id):
    if request.method == "POST":
        # answer = {
        #     "question_id": ObjectId(question_id),
        #     "text": request.form.get("text"),
        #     "username": session["user"]
        # }
        # mongo.db.answers.insert_one(answer)
        text = request.form.get("text")
        username = session["user"]
        Answer.insert_answer(question_id, text, username)
        # Update answer_count
        mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': 1}})
        return redirect(url_for("answers.view_answers", question_id=question_id))
    

@answers_bp.route("/edit_answer/<answer_id>", methods=["GET", "POST"])
def edit_answer(answer_id):
    question_id = Answer.find_ques_id_from_ans_id(answer_id)

    if request.method == "POST":
        text = request.form.get("text")
        username = session["user"]
        Answer.edit_answer(answer_id, question_id, text, username)
        return redirect(url_for("answers.view_answers", question_id=question_id))
    
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    answers = Answer.find_answers_by_question_id(question_id)
    return render_template("edit_answer.html", question=question, answers=answers, answer_id=ObjectId(answer_id))


@answers_bp.route("/delete_answer/<answer_id>")
def delete_answer(answer_id):
    # question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]
    question_id = Answer.find_ques_id_from_ans_id(answer_id)
    # Update answer_count
    mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': -1}})
    # mongo.db.answers.delete_one({"_id": ObjectId(answer_id)})
    Answer.delete_answer(answer_id)
    flash("Answer deleted")
    return redirect(url_for("answers.view_answers", question_id=question_id))