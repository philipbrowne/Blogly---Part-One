"""Blogly application."""

from flask import Flask, request, render_template,  redirect, flash, session
from models import db, connect_db, User, Post
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import asc, desc, func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dogsaregreat1999'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.debug = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.errorhandler(404)
def not_found(e):
    flash(f'Error: {e}', 'error')
    return render_template('404.html')


@app.route('/')
def create_user():
    """Redirect to a List of Users"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    # Last 5 Posts
    posts = Post.query.order_by(desc(Post.created_at)).limit(5).all()
    return render_template('home.html', users=users, posts=posts)


@app.route('/users')
def list_users():
    """Show all users"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('list.html', users=users)


@app.route('/users/<int:user_id>')
def user_details(user_id):
    """Show Details for User"""
    user = User.query.get_or_404(user_id)
    return render_template('details.html', user=user)


@app.route('/users/new')
def new_user_form():
    """Show an add form for users"""
    return render_template('new_user.html')


@app.route('/users/new', methods=['POST'])
def add_new_user():
    """Adds new user to Blogly Database"""
    if request.form['first_name'] and request.form['last_name']:
        flash('Created New User!', 'success')
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        if request.form['image_url']:
            image_url = request.form['image_url']
        else:
            image_url = 'https://randomuser.me/api/portraits/lego/1.jpg'
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()
    else:
        flash('Sorry could not create new user - please try again', 'error')
    return redirect('/users')


@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):
    """Shows a form to edit user details"""
    id = user_id
    user = User.query.get(id)
    return render_template('edit_user.html', id=id, user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def edit_user(user_id):
    """Process the edit form, returning the user to the /users page"""
    user = User.query.get_or_404(user_id)
    if request.form['first_name'] or request.form['last_name'] or request.form['image_url']:
        if request.form['first_name']:
            user.first_name = request.form['first_name']
        if request.form['last_name']:
            user.last_name = request.form['last_name']
        if request.form['image_url']:
            user.image_url = request.form['image_url']
        flash(f'Made changes to {user.full_name}', 'success')
        db.session.add(user)
        db.session.commit()
    else:
        flash('Did not make any changes', 'error')
    return redirect('/users')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete the user."""
    user = User.query.get_or_404(user_id)
    if user:
        flash(f'Deleted User: {user.full_name}', 'success')
        User.query.filter_by(id=user_id).delete()
        db.session.commit()
    else:
        flash('Could not delete user - please try again', 'error')
    return redirect('/users')


@app.route('/users/<int:user_id>/posts/new')
def new_post_form(user_id):
    """Show form to add a post for that user."""
    user = User.query.get_or_404(user_id)
    return render_template('new_post.html', user=user)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show post for corresponding Post Id"""
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template('post_details.html', post=post, user=user)


@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    """Show form to edit a post, and to cancel (back to user page)."""
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template('edit_post.html', post=post, user=user)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_new_post(user_id):
    """Handle add form; add post and redirect to the user detail page."""
    user = User.query.get_or_404(user_id)
    if request.form['title'] and request.form['content']:
        title = request.form['title']
        flash(f'Created new post: {title}', 'success')
        content = request.form['content']
        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
    else:
        flash('Could not make post - please try again', 'error')
    return redirect(f'/users/{user_id}')


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    """Handle editing of a post. Redirect back to the post view."""
    post = Post.query.get_or_404(post_id)
    user = post.user
    if request.form['title'] or request.form['content']:
        if request.form['title']:
            post.title = request.form['title']
        if request.form['content']:
            post.content = request.form['content']
        flash(f'Edited post: {post.title}', 'success')
        db.session.add(post)
        db.session.commit()
    else:
        flash('Did not make any changes', 'error')
    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete the post."""
    post = Post.query.get_or_404(post_id)
    if post:
        user = post.user
        flash(f'Deleted Post ({post.title})', 'success')
        Post.query.filter_by(id=post_id).delete()
        db.session.commit()
    else:
        flash('Could not delete post', 'error')
    return redirect(f'/users/{user.id}')
