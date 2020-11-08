from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from application import db
from application.models import Post, Comment
from application.posts.forms import PostForm, ResponseForm

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Váša otázka bola vytvorená a zverejnená', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='Opýtať sa otázku', form=form, legend='Opýtajte sa otázku')


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = ResponseForm()
    return render_template('post.html', post_id=post_id, title=post.title, post=post, form=form)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Váša otázka bola úspešne upravená', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Upraviť otázku', form=form, legend='Upravte svoju otázku')


@posts.route('/post/<int:post_id>/comments', methods=['POST'])
@login_required
def add_post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = ResponseForm()
    if form.validate_on_submit():
        comment = Comment(content=form.message.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Odpoved bola pridana', 'success')
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Vaša otázka bola vymazaná', 'success')
    return redirect(url_for('main.home'))
