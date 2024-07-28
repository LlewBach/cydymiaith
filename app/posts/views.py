from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.core.models import Core
from app.posts.models import Post
from app.groups.models import Group


posts_bp = Blueprint('posts', __name__, template_folder='../templates')


# Docstrings written by GPT4o and edited by myself.
@posts_bp.route("/get_posts", methods=["GET", "POST"])
def get_posts():
    """
    Displays a list of posts, either all or filtered by specified criteria.

    On a GET request, this function retrieves all available posts along with
    associated categories and groups that are relevant based on the current
    user's role and username. It renders the posts template to display these
    posts.

    On a POST request, it processes form data to filter posts based on selected
    categories and groups. It then retrieves and renders the posts template
    with this filtered list of posts.

    Returns:
        Response: Renders the 'posts.html' template with variables for the list
        of posts, categories, and groups available to the user, as well as any
        active query parameters used for filtering.
    """
    categories = Core.get_categories()
    posts, query = Post.get_list(None, None)
    if current_user.is_authenticated:
        groups = Group.get_groups_by_role(
            current_user.role, current_user.username)
    else:
        groups = []

    if request.method == "POST":
        category = request.form.get("category")
        group_id = request.form.get("group")
        posts, query = Post.get_list(category, group_id)

    return render_template(
        "posts.html",
        posts=posts,
        categories=categories,
        groups=groups,
        query=query
        )


@posts_bp.route("/make_post", methods=["GET", "POST"])
@login_required
def make_post():
    """
    Handles the creation of a new post and renders the make_post template.

    On a GET request, this function renders the 'make_post.html' template with
    the necessary data for creating a post, including a list of categories and
    groups relevant to the current user's role and username. This provides a
    form for users to submit a new post.

    On a POST request, it captures the form data to insert a new post into the
    database, including the username, selected category, group ID, title, and
    description of the post. Upon successful insertion, it flashes a success
    message and redirects the user to the 'get_posts' view to view all posts.

    Returns:
        Response:
            - Renders the 'make_post.html' template with options for categories
            and groups on a GET request.
            - Redirects to the 'get_posts' view with a success message on a
            POST request, indicating successful post creation.
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
    categories = Core.get_categories()
    return render_template(
        "make_post.html",
        categories=categories,
        groups=groups
        )


def user_owns_post_or_admin(f):
    """
    Decorator to ensure that the current user either owns the post or has
    'Admin' privileges.

    This decorator is designed to restrict access to certain view functions
    that manipulate a post. It checks if the current user is either the owner
    of the post (based on the username associated with the post) or has an
    'Admin' role. If neither condition is met, it flashes an unauthorized
    access error message and redirects the user to their profile page. If the
    specified post does not exist or no post_id is provided, it redirects to
    the posts listing page with an error message.

    Args:
        f (function): The view function to which the decorator is applied.

    Returns:
        function: The wrapped function with added authorization checks, or
        redirections if checks fail.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        post_id = kwargs.get('post_id')
        post = Post.find_by_id(post_id)
        if post is None:
            flash("Post not specified.", "error")
            return redirect(url_for('posts.get_posts'))
        if (current_user.username != post['username'] and
                current_user.role != 'Admin'):
            flash("You are not authorized to do this.", "error")
            return redirect(
                url_for('auth.profile', username=current_user.username))
        return f(*args, **kwargs)
    return wrapper


@posts_bp.route("/edit_post", defaults={"post_id": None})
@posts_bp.route("/edit_post/<post_id>", methods=["GET", "POST"])
@login_required
@user_owns_post_or_admin
def edit_post(post_id):
    """
    Handles the editing of an existing post and renders the edit_post template.

    On a GET request, this function retrieves the post by its ID and renders
    the 'edit_post.html' template with the post's current data, including
    available categories and groups based on the user's role.

    On a POST request, it captures updated post details from the form data
    (title, description, category, and group) and updates the post in the
    database. After updating, it flashes a success message and redirects the
    user to the 'get_posts' view to see all posts.

    Args:
        post_id (str, optional): The ID of the post to be edited. If not
        provided, a GET request leads to the posts listing.

    Returns:
        Response:
            - On GET: Renders the 'edit_post.html' template with the post's
            details and options for categories and groups.
            - On POST: Updates the post and redirects to 'get_posts' view with
            a success message.
    """
    if request.method == "POST":
        username = current_user.username
        category = request.form.get("category")
        group_id = request.form.get("group")
        title = request.form.get("title")
        description = request.form.get("description")
        Post.update_post(
            post_id, username, category, group_id, title, description
            )
        flash("Post Updated")
        return redirect(url_for('posts.get_posts'))

    groups = Group.get_groups_by_role(current_user.role, current_user.username)
    categories = Core.get_categories()
    post = Post.find_by_id(post_id)
    return render_template(
        "edit_post.html",
        post=post,
        groups=groups,
        categories=categories
        )


@posts_bp.route("/delete_post", defaults={"post_id": None})
@posts_bp.route("/delete_post/<post_id>")
@login_required
@user_owns_post_or_admin
def delete_post(post_id):
    """
    Deletes a post from the database and redirects to the get_posts view.

    This function deletes the specified question from the database. It then
    flashes a success message to the user and redirects to the get_posts view.

    Args:
        post_id (str): The ID of the post to be deleted.

    Returns:
        Response: Redirects to the get_posts view after deleting the post.
    """
    Post.delete_post(post_id)
    flash("Post Deleted")
    return redirect(url_for("posts.get_posts"))
