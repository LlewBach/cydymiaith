from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import datetime
import humanize
import pytz
from app import mongo

answers_bp = Blueprint('answers', __name__, template_folder='../templates/answers')

@answers_bp.route("/view_answers/<question_id>")
def view_answers(question_id):
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    creation_time = question['_id'].generation_time.replace(tzinfo=pytz.utc)
    question['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)
    answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
    answer_count = len(answers)
    return render_template("view_answers.html", question=question, answers=answers, answer_count=answer_count)


@answers_bp.route("/answer/<question_id>", methods=["GET", "POST"])
def answer(question_id):
    if request.method == "POST":
        answer = {
            "question_id": ObjectId(question_id),
            "text": request.form.get("text"),
            "username": session["user"]
        }
        mongo.db.answers.insert_one(answer)
        # Update answer_count
        mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': 1}})
        return redirect(url_for("answers.view_answers", question_id=question_id))
    

@answers_bp.route("/edit_answer/<answer_id>", methods=["GET", "POST"])
def edit_answer(answer_id):
    question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]

    if request.method == "POST":
        answer = {
            "question_id": question_id,
            "text": request.form.get("text"),
            "username": session["user"]
        }
        mongo.db.answers.update_one({"_id": ObjectId(answer_id)}, {"$set": answer})
        return redirect(url_for("answers.view_answers", question_id=question_id))
    
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
    return render_template("edit_answer.html", question=question, answers=answers, answer_id=ObjectId(answer_id))


@answers_bp.route("/delete_answer/<answer_id>")
def delete_answer(answer_id):
    question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]
    # Update answer_count
    mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': -1}})
    mongo.db.answers.delete_one({"_id": ObjectId(answer_id)})
    flash("Answer deleted")
    return redirect(url_for("answers.view_answers", question_id=question_id))