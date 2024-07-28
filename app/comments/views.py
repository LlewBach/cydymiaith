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
    Renders the view_comments template for a specific post.

    This function retrieves a post and its associated comments from the
    database. It also sets the relative time since the post was created and
    counts the number of comments. If the post exists, it renders the
    view_comments template with the post, comments, and the total comment
    count. If no post_id is provided or if the post does not exist, it
    redirects to a general posts page with an appropriate error message.

    Args:
        post_id (str, optional): The ID of the post for which comments are to
        be viewed.

    Returns:
        Response:
            - Renders the 'view_comments.html' template with the post, its
            comments, and the count of comments if the post is found.
            - Redirects to the 'posts.get_posts' page with an error message if
            the post is not found or the post_id is not specified.
    """
    if post_id:
        post = Post.find_by_id(post_id)
        if post is None:
            flash("Post Not Found")
            return redirect(url_for("posts.get_posts"))
        Post.set_time_ago(post)
        comments = Comment.find_comments_by_post_id(post_id)
        comment_count = Comment.count_comments(comments)

        return render_template(
            "view_comments.html",
            post=post,
            comments=comments,
            comment_count=comment_count
            )
    else:
        flash("Post Not Specified")
        return redirect(url_for("posts.get_posts"))


@comments_bp.route("/comment", defaults={"post_id": None})
@comments_bp.route("/comment/<post_id>", methods=["GET", "POST"])
@login_required
def comment(post_id):
    """
    Manages the addition of comments to a specific post.

    On POST requests, it retrieves the comment text from the form, saves the
    new comment in the database associated with the post, and updates the
    comment count for the post. A success message is then flashed to the user,
    and they are redirected to the view_comments page to see their new comment
    and all others.

    Args:
        post_id (str, optional): The ID of the post to which the comment is to
        be added. If not provided, a message is flashed, and the user is
        redirected.

    Returns:
        Response:
            - Redirects to the view_comments page for the specified post_id to
            display the newly added comment and existing comments.
            - Redirects to the posts overview page with an error message if no
            post is found or the post_id is not specified.
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
    """
    Decorator to check if the current user is authorized to perform actions on
    a specific comment.

    This decorator verifies that the current user either owns the comment or
    has an 'Admin' role before allowing access to the target function. If the
    comment does not exist or if the user does not have the appropriate
    permissions, it flashes an error message and redirects the user
    accordingly.

    It first checks if the comment exists based on a 'comment_id' extracted
    from the route parameters. If the comment exists, it then checks if the
    current user is the owner of the comment or an admin. If neither condition
    is met, it prevents access by redirecting the user with an error message.

    Args:
        f (function): The wrapped view function.

    Returns:
        function: The wrapped function with added authorization checks, or
        redirections if checks fail.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        comment_id = kwargs.get('comment_id')
        comment = Comment.find_by_id(comment_id)
        if comment is None:
            flash("Comment Not Specified", "error")
            return redirect(url_for('posts.get_posts'))
        if (current_user.username != comment['username'] and
                current_user.role != 'Admin'):
            flash("You are not authorized to do this.", "error")
            return redirect(
                url_for('auth.profile', username=current_user.username)
                )
        return f(*args, **kwargs)
    return wrapper


@comments_bp.route("/edit_comment", defaults={"comment_id": None})
@comments_bp.route("/edit_comment/<comment_id>", methods=["GET", "POST"])
@login_required
@user_owns_comment_or_admin
def edit_comment(comment_id):
    """
    Handles the editing of an existing comment and updates the database.

    On a GET request, it renders the edit_comment template with the current
    comment details. On a POST request, it updates the comment in the database
    with the provided text, flashes a success message to the user, and
    redirects to the view_comments template to display the post with the
    updated list of comments.

    Args:
        comment_id (str): The ID of the comment to be edited.

    Returns:
        Response:
            - Renders the edit_comment.html template with the current comment
            details on a GET request.
            - Redirects to the view_comments template to display the post with
            the updated comment on a POST request.
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

    return render_template(
        "edit_comment.html",
        post=post,
        comments=comments,
        comment_id=ObjectId(comment_id)
        )


@comments_bp.route("/delete_comment", defaults={"comment_id": None})
@comments_bp.route("/delete_comment/<comment_id>")
@login_required
@user_owns_comment_or_admin
def delete_comment(comment_id):
    """
    Deletes a specific comment from the database and updates the associated
    post's comment count.

    This function deletes a comment from the database, decreases the comment
    count of the associated post, flashes a success message to the user, and
    redirects to the view_comments template to display the updated list of
    comments.

    Args:
        comment_id (str): The ID of the comment to be deleted.

    Returns:
        Response: Redirects to the view_comments template to display the
        updated list of comments.
    """
    post_id = Comment.find_post_id(comment_id)
    Post.decrease_comment_count(post_id)
    Comment.delete_comment(comment_id)
    flash("Comment Deleted")

    return redirect(url_for("comments.view_comments", post_id=post_id))
