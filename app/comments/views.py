from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app.comments.models import Comment
from app.posts.models import Post


comments_bp = Blueprint('comments', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@comments_bp.route("/view_comments", defaults={"post_id": None})
@comments_bp.route("/view_comments/<post_id>")
def view_comments(post_id):
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
    if post_id:
        post = Post.find_by_id(post_id)
        if post == None:
            flash("Post Not Found")
            return redirect(url_for("posts.get_posts"))
        Post.set_time_ago(post)
        comments = Comment.find_comments_by_post_id(post_id)
        comment_count = Comment.count_comments(comments)

        return render_template("view_comments.html", post=post, comments=comments, comment_count=comment_count)
    else:
        flash("Post Not Specified")
        return redirect(url_for("posts.get_posts"))


@comments_bp.route("/comment", defaults={"post_id": None})
@comments_bp.route("/comment/<post_id>", methods=["GET", "POST"])
@login_required
def comment(post_id):
    """
    Adds an answer to a specific question and updates the database.

    On a POST request, it retrieves the answer text from the form, inserts the answer into the database, increases the answer count for the question, flashes a success message to the user, and redirects to the view_answers template to display the updated list of answers.

    Args:
        question_id (str): The ID of the question to which the answer is to be added.

    Returns:
        Response: Redirects to the view_answers template to display the updated list of answers.
    """
    if post_id:
        found_post = Post.find_by_id(post_id)
        if not found_post:
            flash("No Post Found")
            return redirect(url_for("posts.get_posts"))

        if request.method == "POST":
            text = request.form.get("text")
            username = current_user.username
            Comment.insert_comment(post_id, text, username)
            Post.increase_comment_count(post_id)
            flash("Comment added")

            return redirect(url_for("comments.view_comments", post_id=post_id))
    else:
        flash("Post Not Specified")
        return redirect(url_for("posts.get_posts"))
    

def user_owns_comment_or_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        comment_id = kwargs.get('comment_id')
        comment = Comment.find_by_id(comment_id)
        if comment is None:
            flash("Comment Not Specified", "error")
            return redirect(url_for('posts.get_posts'))
        if current_user.username != comment['username'] and current_user.role != 'Admin':
            flash("You are not authorized to do this.", "error")
            return redirect(url_for('auth.profile', username=current_user.username))
        return f(*args, **kwargs)
    return wrapper


@comments_bp.route("/edit_comment", defaults={"comment_id": None})
@comments_bp.route("/edit_comment/<comment_id>", methods=["GET", "POST"])
@login_required
@user_owns_comment_or_admin
def edit_comment(comment_id):
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
    post_id = Comment.find_post_id(comment_id)

    if request.method == "POST":
        text = request.form.get("text")
        username = current_user.username
        Comment.edit_comment(comment_id, post_id, text, username)
        flash("Comment Edited")

        return redirect(url_for("comments.view_comments", post_id=post_id))
    
    post = Post.find_by_id(post_id)
    comments = Comment.find_comments_by_post_id(post_id)

    return render_template("edit_comment.html", post=post, comments=comments, comment_id=ObjectId(comment_id))


@comments_bp.route("/delete_comment", defaults={"comment_id": None})
@comments_bp.route("/delete_comment/<comment_id>")
@login_required
@user_owns_comment_or_admin
def delete_comment(comment_id):
    """
    Deletes a specific answer from the database and updates the associated question's answer count.

    This function deletes an answer from the database, decreases the answer count of the associated question, flashes a success message to the user, and redirects to the view_answers template to display the updated list
    of answers.

    Args:
        answer_id (str): The ID of the answer to be deleted.

    Returns:
        Response: Redirects to the view_answers template to display the updated list of answers.
    """
    post_id = Comment.find_post_id(comment_id)
    Post.decrease_comment_count(post_id)
    Comment.delete_comment(comment_id)
    flash("Comment Deleted")
    
    return redirect(url_for("comments.view_comments", post_id=post_id))