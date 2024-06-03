import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_questions")
def get_questions():
    questions = mongo.db.questions.find()
    return render_template("questions.html", questions=questions)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("login"))
        
        register = {
            "username": request.form.get("username").lower(),
            # can customize hash and salt methods, this standard
            # if second field to confirm password, would confirm before here
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Croeso, {}".format(request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                flash("Incorrect username and/or password")
                return redirect(url_for('login'))
            
        else:
            flash("Incorrect username and/or password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>")
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("Logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/ask_question", methods=["GET", "POST"])
def ask_question():
    if request.method == "POST":
        question = {
            "username": session["user"],
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "timestamp": None,
            "answer_count": 0
        }
        mongo.db.questions.insert_one(question)
        flash("Question posted to community:)")
        return redirect(url_for('get_questions'))

    return render_template("ask_question.html")


@app.route("/edit_question/<question_id>", methods=["GET", "POST"])
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
        return redirect(url_for('get_questions'))
    
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    return render_template("edit_question.html", question=question)


@app.route("/delete_question/<question_id>")
def delete_question(question_id):
    mongo.db.questions.delete_one({"_id": ObjectId(question_id)})
    flash("Question deleted")
    return redirect(url_for("get_questions"))


@app.route("/view_answers/<question_id>")
def view_answers(question_id):
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
    answer_count = len(answers)
    return render_template("view_answers.html", question=question, answers=answers, answer_count=answer_count)


@app.route("/answer/<question_id>", methods=["GET", "POST"])
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
        return redirect(url_for("view_answers", question_id=question_id))
    

@app.route("/edit_answer/<answer_id>", methods=["GET", "POST"])
def edit_answer(answer_id):
    question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]

    if request.method == "POST":
        answer = {
            "question_id": question_id,
            "text": request.form.get("text"),
            "username": session["user"]
        }
        mongo.db.answers.update_one({"_id": ObjectId(answer_id)}, {"$set": answer})
        return redirect(url_for("view_answers", question_id=question_id))
    
    question = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
    answers = list(mongo.db.answers.find({"question_id": ObjectId(question_id)}))
    return render_template("edit_answer.html", question=question, answers=answers, answer_id=ObjectId(answer_id))


@app.route("/delete_answer/<answer_id>")
def delete_answer(answer_id):
    question_id = mongo.db.answers.find_one({"_id": ObjectId(answer_id)})["question_id"]
    # Update answer_count
    mongo.db.questions.update_one({'_id': ObjectId(question_id)}, {'$inc': {'answer_count': -1}})
    mongo.db.answers.delete_one({"_id": ObjectId(answer_id)})
    flash("Answer deleted")
    return redirect(url_for("view_answers", question_id=question_id))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
    