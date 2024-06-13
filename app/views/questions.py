from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import datetime
import humanize
import pytz

from app import mongo


questions_bp = Blueprint('questions', __name__, template_folder='../templates')


@questions_bp.route("/get_questions")
def get_questions():
    questions = list(mongo.db.questions.find().sort("_id", -1))
    for question in questions:
        creation_time = question['_id'].generation_time.replace(tzinfo=pytz.utc)
        question['time_ago'] = humanize.naturaltime(datetime.now(pytz.utc) - creation_time)

    return render_template("questions.html", questions=questions)


@questions_bp.route("/ask_question", methods=["GET", "POST"])
def ask_question():
    if request.method == "POST":
        question = {
            "username": session["user"],
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "answer_count": 0
        }
        mongo.db.questions.insert_one(question)
        flash("Question posted to community:)")
        return redirect(url_for('questions.get_questions'))

    return render_template("ask_question.html")


@questions_bp.route("/edit_question/<question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "POST":
        submit = {
            "username": session["user"],
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "timestamp": None
        }
        mongo.db.questions.update_one({"_id": ObjectId(question_id)}, {"$set": submit})
        flash("Question updated")
        return redirect(url_for('questions.get_questions'))
    
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    return render_template("edit_question.html", question=question)


@questions_bp.route("/delete_question/<question_id>")
def delete_question(question_id):
    mongo.db.questions.delete_one({"_id": ObjectId(question_id)})
    flash("Question deleted")
    return redirect(url_for("questions.get_questions"))