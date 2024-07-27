from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.posts.models import Post
from app.groups.models import Group


posts_bp = Blueprint('posts', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@posts_bp.route("/get_posts", methods=["GET", "POST"])
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
    categories = Post.get_categories()
    posts, query = Post.get_list(None, None)
    groups = Group.get_groups_by_role(current_user.role, current_user.username) if current_user.is_authenticated else []

    if request.method == "POST":
        category = request.form.get("category")
        group_id = request.form.get("group")
        posts, query = Post.get_list(category, group_id)

    return render_template("posts.html", posts=posts, categories=categories, groups=groups, query=query)


@posts_bp.route("/make_post", methods=["GET", "POST"])
@login_required
def make_post():
    """
    Handles the creation of a new question and renders the make_post template.

    On a GET request, this function renders the make_post template with the necessary
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
        Post.insert_post(username, category, group_id, title, description)
        flash("Post Published")
        return redirect(url_for('posts.get_posts'))

    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    categories = Post.get_categories()
    return render_template("make_post.html", categories=categories, groups=groups)


def user_owns_post_or_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        post_id = kwargs.get('post_id')
        post = Post.find_by_id(post_id)
        if post == None:
            flash("Post not specified.", "error")
            return redirect(url_for('posts.get_posts'))
        if current_user.username != post['username'] and current_user.role != 'Admin':
            flash("You are not authorized to do this.", "error")
            return redirect(url_for('auth.profile', username=current_user.username))
        return f(*args, **kwargs)
    return wrapper


@posts_bp.route("/edit_post", defaults={"post_id": None})
@posts_bp.route("/edit_post/<post_id>", methods=["GET", "POST"])
@login_required
@user_owns_post_or_admin
def edit_post(post_id):
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
        Post.update_post(post_id, username, category, group_id, title, description)
        flash("Post Updated")
        return redirect(url_for('posts.get_posts'))
    
    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    categories = Post.get_categories()
    post = Post.find_by_id(post_id)
    return render_template("edit_post.html", post=post, groups=groups, categories=categories)


@posts_bp.route("/delete_post", defaults={"post_id": None})
@posts_bp.route("/delete_post/<post_id>")
@login_required
@user_owns_post_or_admin
def delete_post(post_id):
    """
    Deletes a question from the database and redirects to the get_posts view.

    This function deletes the specified question from the database. It then flashes a success message
    to the user and redirects to the get_posts view.

    Args:
        question_id (str): The ID of the question to be deleted.

    Returns:
        Response: Redirects to the get_posts view after deleting the question.
    """
    Post.delete_post(post_id)
    flash("Post Deleted")
    return redirect(url_for("posts.get_posts"))